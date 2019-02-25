#! /usr/bin/env python3
import yaml
import numpy as np
import math
from datetime import datetime
import matplotlib.pyplot as plt

np.random.seed(42)

SECONDS_IN_YEAR = 60*60*24*365
SECONDS_IN_DAY = 60*60*24
SECONDS_IN_HOUR = 60*60
SECONDS_IN_MINUTE = 60

# state for reactive workload
_lambda_set = None
_reactive_hour = None
_current_hour_P = None
transmits = 0

class EnergyHarvestingSimulator:
    def _init_energy():
        # initialize energy for sleep and active
        self.sleep_power = self.workload_config['sleep_current_A'] /\
                self.design_config['boost_efficiency']* \
                self.design_config['operating_voltage_V']
        self.event_energy = self.workload_config['event_energy_J'] /\
                self.design_config['boost_efficiency']


        self.event_period_full = workload_config['event_period_s']
        self.event_period_min = workload_config['event_period_min_s']

        self.atomic = workload_config['atomic']

        # initialize energy for primary and secondary
        if self.primary_config is not None:
            self.has_primary = True
            #if 'volume_L' in primary_config and 'density_Whpl' in primary_config:
            #    primary_volume = primary_config['volume_L']
            #    primary_density = primary_config['density_WhpL']
            #    primary_energy = primary_energy_max = primary_volume * primary_density * SECONDS_IN_HOUR
            #    primary_leakage_energy = primary_energy * primary_config['leakage_percent_year']/100/SECONDS_IN_YEAR
            self.primary_energy = self.primary_energy_max =\
                    self.primary_config['capacity_mAh']\
                        * 1E-3 * self.primary_config['nominal_voltage_V'] \
                        * SECONDS_IN_HOUR
            self.primary_leakage_energy = self.primary_energy *\
                    self.primary_config['leakage_percent_year']\
                        / 100 / SECONDS_IN_YEAR
        else:
            self.has_primary = False
            self.primary_energy = 0
            self.primary_energy_max = 0
            self.primary_leakage_energy = 0

        if self.secondary_config is not None:
            # using a battery:
            if self.secondary_config['type'] == 'battery':
                self.secondary_energy_max = \
                        self.secondary_config['capacity_mAh'] * 1E-3 *\
                        self.secondary_config['nominal_voltage_V'] * SECONDS_IN_HOUR
                if 'leakage_power_W' in self.secondary_config:
                    # second level simulation, so multiply by 1
                    self.secondary_leakage_energy = self.secondary_config['leakage_power_W'] * 1
                else:
                    self.secondary_leakage_energy = self.secondary_config['capacity_mAh'] *\
                    1E-3 / self.secondary_config['leakage_constant'] *\
                    self.secondary_config['nominal_voltage_V']
                self.secondary_energy_up = self.secondary_config['secondary_max_percent'] \
                        / 100 * self.secondary_energy_max
                self.secondary_energy_min = self.secondary_config['secondary_min_percent'] \
                        / 100 * self.secondary_energy_max
                assert(self.secondary_energy_max >= self.secondary_energy_up)
                assert(self.secondary_energy_up >= self.secondary_energy_min)
            # using a capacitor:
            elif self.secondary_config['type'] == 'capacitor':
                self.secondary_energy_max = self.secondary_config['capacity_J']
                self.secondary_leakage_energy = self.secondary_config['leakage_power_W'] * 1
                self.secondary_energy_up = self.secondary_energy_min = self.secondary_config['min_capacity_J']

            # either start at defined percent, or start empty
            if 'secondary_start_percent' in self.secondary_config:
                self.secondary_energy = self.secondary_energy_max * \
                    self.secondary_config['secondary_start_percent']/100
            else:
                self.secondary_energy = self.secondary_energy_min
        # secondary_config is None
        else:
            self.secondary_leakage_energy = self.secondary_energy = \
                    self.secondary_energy_max = self.secondary_energy_up = \
                    self.secondary_energy_min = 0

        # ESR losses
        event_current = self.event_energy / self.event_period_full / self.design_config['operating_voltage_V']
        esr_power = self.event_current**2 * self.secondary_config['esr_ohm']
        self.event_energy += esr_power * self.event_period_full
        # if we couldn't possibly ever perform any work throw an error
        if (self.atomic and (self.event_energy > self.primary_energy_max + self.secondary_energy_max - self.secondary_energy_min)\
                or self.event_period_min > 1)\
                or self.primary_energy_max + self.secondary_energy_max <= self.workload_config['startup_energy_J']:
            print(self.atomic and self.event_energy > self.secondary_energy_max - self.secondary_energy_min)
            print(self.event_energy, self.secondary_energy_max - self.secondary_energy_min)
            print(self.event_period_min > 1)
            print(self.secondary_energy_max <= self.workload_config['startup_energy_J'])
            print('ERROR: event either takes too long or takes too much energy with this config to be performed in one step')
            exit(1)

    def __init__(platform_config, workload_config, dataset_config):
        self.platform_config = platform_config
        self.workload_config = workload_config
        self.dataset_config = dataset_config
        self.design_config = platform_config['design_config']
        # load secondary/primary/harvester configs, if they exist
        if self.design_config['using_secondary']:
            self.secondary_config = self.platform_config['secondary_config']
        else:
            self.secondary_config = None
        if self.design_config['using_primary']:
            self.primary_config = self.platform_config['primary_config']
        else:
            self.primary_config = None
        if self.design_config['using_harvester']:
            self.harvester_config = self.platform_config['harvester_config']
        else:
            self.harvester_config = None

        _init_energy()

        # load energy trace
        trace_fname = self.dataset_config['filename']
        self.trace = np.load(trace_fname)
        self.trace_resolution = self.dataset_config['resolution_s']
        self.trace_unit = self.dataset_config['unit']

        # prepare light dataset
        self.trace_start_time = lights[0].astype('datetime64[s]')
        self.trace_start_seconds = int((self.trace_start_time - self.trace_start_time.astype('datetime64[D]')) / np.timedelta64(1, 's'))
        self.trace = self.trace[1:]
        seconds = np.arange(self.trace.size*self.trace_resolution)

        # prepare solar values
        if self.harvester_config['type'] is 'solar':
            if 'area_cm2' in self.harvester_config:
                self.solar_area = self.harvester_config['area_cm2']
            #else: solar_area = 2 * 100 * primary_volume ** (2.0/3.0)
            if self.trace_unit is not 'uW/cm2':
                print('Incorrect energy trace unit')
                exit(1)
        else:
            print("Currently unsupported energy trace")
            exit(1)



def is_time_to_transmit(workload, second):
    global _lambda_set
    global _reactive_hour
    global _current_hour_P
    global transmits
    if workload['type'] == 'periodic':
        if int(second) % int(workload['period_s']) == 0:
            return 1
        return 0
    elif workload['type'] == 'reactive':
        if _lambda_set is None or _lambda_set.size == 0:
            # not initialized yet!
            _lambda_set = np.ceil(workload['lambda'] * np.load(workload['curve'])).astype(int)
        # get hour of day from second
        remainder = second % SECONDS_IN_DAY
        hour = int(math.floor(remainder / SECONDS_IN_HOUR))
        if hour != _reactive_hour:
            transmits = 0
            _reactive_hour = hour
            # get probability of event happening each second in this hour
            p = np.random.poisson(_lambda_set[hour], 1)
            _current_hour_P = p / SECONDS_IN_HOUR #np.random.poisson(_lambda_set[hour], 1) / SECONDS_IN_HOUR
        transmit = np.random.random() <= _current_hour_P
        transmits += transmit
        return transmit
    elif workload['type'] == 'random':
        return np.random.random() <= (1 / workload['period_s'])

# for a given remaining event period and energy,
# return period, energy consumed, and if finished on this cycle
def perform_event(available_time, available_energy, period_remaining, energy_remaining):
    if energy_remaining <= available_energy:
        # if energy store has enough energy
        if period_remaining <= available_time:
            # and we can do the operation in the available period
            return period_remaining, energy_remaining, 1
        else:
            # we can't, so do some amount of work
            e = available_time * (energy_remaining/period_remaining)
            return available_time, e, 0

    else:
        t = available_energy / (energy_remaining/period_remaining)
        if t <= available_time:
            return t, t * energy_remaining / period_remaining, 0
        else:
            return available_time, available_time * energy_remaining / period_remaining, 0



def simulate(config, workload, lights):

    # begin simulation
    secondary_soc = []
    primary_soc = []
    primary_discharge = 0
    solar_powers = []
    out_powers = []
    online = [0]
    missed = []
    event_ttc = []
    used_energy = secondary_energy_min - secondary_energy
    possible_energy = 0
    # state to keep track of ongoing events
    currently_performing = False
    event_period_remaining = 0
    event_energy_remaining = 0
    actual_period = 0
    #events_completed = 0
    # wait for secondary to charge
    charge_hysteresis = False;
    for second in seconds:

        ##
        ## INCOMING ENERGY
        ##
        # energy from solar panel:
        incoming_energy = lights[math.floor(second / dataset_config['resolution_s'])] * 1E-6 * solar_area \
            * solar_config['efficiency'] * design_config['frontend_efficiency']
        #solar_powers.append(incoming_energy)
        possible_energy += incoming_energy

        # charge secondary if possible
        secondary_energy += incoming_energy

        # reset secondary to max if full
        if secondary_energy > secondary_energy_max:
            #wasted_energy += secondary_energy - secondary_energy_max
            secondary_energy = secondary_energy_max
        # if charged enough
        if charge_hysteresis and secondary_energy >= secondary_energy_up:
            charge_hysteresis = False

        ###
        ### OUTGOING ENERGY
        ###
        outgoing_startup_energy = 0
        outgoing_event_energy = 0
        outgoing_sleep_energy = 0
        def remaining_secondary_energy():
            return secondary_energy - secondary_energy_min - outgoing_startup_energy - outgoing_event_energy - outgoing_sleep_energy
        def outgoing_energy():
            return outgoing_startup_energy + outgoing_event_energy + outgoing_sleep_energy
        period_sleep = 1
        currently_online = online[-1] == 1

        # if offline, need to pay startup cost
        # don't go online until we can do useful work
        if not currently_online and not charge_hysteresis:
            if workload_config['name'] == 'ota_update':
                energy_to_turn_on = workload_config['startup_energy_J'] + event_energy/event_period_full * event_period_min
            else:
                energy_to_turn_on = workload_config['startup_energy_J'] + event_energy
            if remaining_secondary_energy() + primary_energy >= energy_to_turn_on:
                outgoing_startup_energy = workload_config['startup_energy_J']
                period_sleep -= workload_config['startup_period_s']
                currently_online = 1

        # if it's time to perform an event
        # if opportunistic, try to send
        if design_config['intermittent_mode'] == 'opportunistic':
            if currently_online:
                actual_period = 0
                currently_performing = 1
                event_energy_remaining = event_energy
                event_period_remaining = event_period_full
            else:
                missed.append(np.array([start_time+second, 1]))
        elif is_time_to_transmit(workload_config, second + start_seconds):
            # we're already working on an event, or we're not online to do
            # event, count it as a miss and try next time
            if currently_performing or not currently_online:
                missed.append(np.array([start_time+second, 1]))
            # reset event energy/period state and start new event
            else:
                actual_period = 0
                currently_performing = 1
                event_energy_remaining = event_energy
                event_period_remaining = event_period_full

        # if we need to work on an event
        if currently_performing and currently_online:
            # calculated expected period, energy, and if finished for this cycle
            if not has_primary:
                used_p, used_e, finished = perform_event(period_sleep, remaining_secondary_energy(), event_period_remaining, event_energy_remaining)
            else:
                used_p, used_e, finished = perform_event(period_sleep, remaining_secondary_energy() + primary_energy, event_period_remaining, event_energy_remaining)
            outgoing_event_energy = used_e
            event_energy_remaining -= used_e
            event_period_remaining -= used_p
            period_sleep -= used_p
            # if we finished the event this iteration
            if finished:
                #events_completed += 1
                actual_period += used_p
                #reset event state variables
                currently_performing = 0
                # successfully completed event
                missed.append(np.array([start_time+second, 0]))
                #events.append(start_time+second)
                event_ttc.append(actual_period)
            # if atomic, count not finishing as failure
            elif atomic:
                currently_performing = 0
                missed.append(np.array([start_time+second, 1]))
        actual_period += 1

        #print(remaining_secondary_energy())
        ###
        ### UPDATE STATE
        ###

        if not has_primary:
            # if we couldn't turn on
            if not currently_online:
                period_on = 0
            # any remaining time is spent sleeping
            # can we sleep the rest of the iteration?
            elif remaining_secondary_energy() > sleep_power * period_sleep:
                outgoing_sleep_energy = sleep_power * period_sleep
                period_on = 1
            # if not, how long can we sleep for?
            else:
                outgoing_sleep_energy  = remaining_secondary_energy()
                period_on = 1 - period_sleep
                period_on += remaining_secondary_energy() / sleep_power
                currently_online = 0
            online.append(period_on)

            secondary_energy -= outgoing_energy()
            used_energy += outgoing_energy()

            if secondary_energy <= secondary_energy_min:
                charge_hysteresis = True
        else:
            online.append(1)

            if charge_hysteresis:
                primary_energy -= outgoing_energy()
                primary_discharge += outgoing_energy()
            else:
                secondary_energy -= outgoing_energy()
                used_energy += outgoing_energy()
                # enter hysteresis if under
                if secondary_energy <= secondary_energy_min:
                    if secondary_energy < 0:
                        used_energy += secondary_energy
                        primary_energy + secondary_energy
                        primary_discharge += abs(secondary_energy)
                    secondary_energy = secondary_energy_min
                    charge_hysteresis = True

            # check if now offline
            # if primary and secondary are dead, note offline
            if primary_energy <= 0:
                break;

        # subtract leakage
        primary_energy -= primary_leakage_energy
        primary_discharge += primary_leakage_energy
        secondary_energy -= secondary_leakage_energy

        secondary_soc.append(secondary_energy)
        primary_soc.append(primary_energy)

    # convert to np array
    missed = np.asarray(missed, dtype='object')
    event_ttc = np.asarray(event_ttc)
    #print('Averages:')
    ##print('  light ' + str(np.mean(lights)) + ' uW/cm^2')
    #print('  solar ' + str(np.mean(solar_powers)) + ' W')
    #print('  secondary: ' + str(secondary_leakage_energy/60) + ' W')
    #print('  primary: ' + str(primary_leakage_energy/60) + ' W')
    #print('  out ' + str(np.mean(out_powers)) + ' W')
    #print('  total ' + str(np.mean(solar_powers) - primary_leakage_energy/60 - secondary_leakage_energy/60 - np.mean(out_powers)) + ' W')
    #print('  Wasted ' + str(wasted_energy))
    #print('  Possibly Collected ' + str(possible_energy))
    ##print('  minimum primary discharge ' + str(primary_leakage_current))

    #plt.figure()
    #plt.plot(np.arange(lights.size), [x for x in lights])
    #print(len(events))
    #plt.figure()
    #plt.plot(seconds, [x for x in secondary_soc])
    #plt.show()
    #plt.plot(seconds, [x*1E3/2.4/3600 for x in offline[1:]])
    #plt.plot(missed[:,0], missed[:,1])
    #plt.figure()
    #plt.plot(seconds, [x*1E3/2.4/3600 for x in primary_soc])
    #plt.show()
    #slope, intercept, _, _, _ = stats.linregress(minutes, primary_soc)
    if has_primary:
        #lifetime_years = (primary_energy_max/ np.mean(primary_discharges))/(SECONDS_IN_YEAR)
        #print (primary_discharge, primary_energy_max)
        lifetime_years = primary_energy_max / (primary_discharge / seconds.size) / SECONDS_IN_YEAR
    else: lifetime_years = -1
    #plt.plot([x for x in minutes], [intercept + slope*x*1E3/2.4/3600 for x in minutes])
    #lifetime_years = minute/60/24/365
    online = np.asarray(online)

    #np.save('seq_no-Ligeiro-c098e5d00047_sim', events)
    return lifetime_years, used_energy, possible_energy, missed[:,1], online, event_ttc

if __name__ == "__main__":
    import argparse
    import importlib


    # Input files for simulation
    parser = argparse.ArgumentParser(description='Energy Harvesting Simulation.')
    parser.add_argument('-c', dest='config_file', default='config.yaml', help='input config file e.g. `config.yaml`')
    parser.add_argument('-w', dest='workload_file', default='workload.yaml', help='input workload config file e.g. `workload.yaml`')
    parser.add_argument('-d', dest='dataset_file', default='dataset.yaml', help='input dataset config file e.g. `dataset.yaml`')
    args = parser.parse_args()

    config = {}
    workload = {}
    dataset = {}
    with open(args.config_file, 'r') as c_file, \
         open(args.workload_file, 'r') as wl_file, \
         open(args.dataset_file, 'r') as d_file:
        try:
            config = yaml.safe_load(c_file)
            workload = yaml.safe_load(wl_file)['workload']
            dataset = yaml.safe_load(d_file)['dataset']
        except yaml.YAMLError as e:
            print(e)
            exit(1)
    print(config)
    print(workload)
    print(dataset)
    exit(0)

    lifetime, used, possible, missed, online, event_ttc = simulate(config, workload, trace)
    print(str(lifetime) + " years")
    print("%.2f/%.2f Joules used" % (used, possible))
    print("%.2f%% events successful" % (100 * (missed.size - np.sum(missed))/missed.size))
    print("%.2f%% of time online" % (100 * np.sum(online) / online.size))
    #print("%.2f%% x expected event time to completion" % (event_ttc / workload.config['event_period_s']))
    print("%.2f%% x expected event time to completion" % (np.average(event_ttc) / workload.config['event_period_s']))


