/* Blink
 */

#include <stdbool.h>
#include <stdint.h>
#include "nrf.h"
#include "nrf_delay.h"
#include "nrf_sdh.h"
#include "nrf_soc.h"
#include "nrf_gpio.h"
#include "nrf_power.h"
#include "nrf_twi_mngr.h"
#include "nrf_log.h"
#include "nrf_log_ctrl.h"
#include "nrf_log_default_backends.h"
#include "nrf_drv_spi.h"
#include "app_timer.h"

#include <openthread/message.h>
#include "simple_thread.h"
#include "thread_ntp.h"
#include "thread_coap.h"
#include "thread_dns.h"
#include "device_id.h"
#include "flash_storage.h"

#include "permacam.h"

#include "hm01b0.h"
#include "ab1815.h"
#include "HM01B0_SERIAL_FULL_8bits_msb_5fps.h"

#include "config.h"

APP_TIMER_DEF(camera_timer);

NRF_TWI_MNGR_DEF(twi_mngr_instance, 5, 0);
static nrf_drv_spi_t spi_instance = NRF_DRV_SPI_INSTANCE(1);

typedef struct{
  bool take_pic;
} permacam_state_t;

permacam_state_t state = {0};

uint8_t enables[7] = {
   HM01B0_ENn,
   MAX44009_EN,
   PIR_EN,
   I2C_SDA,
   I2C_SCL
};

void camera_timer_callback(void* context) {
    state.take_pic = true;
}

void twi_init(const nrf_twi_mngr_t * twi_instance) {
  ret_code_t err_code;

  const nrf_drv_twi_config_t twi_config = {
    .scl                = I2C_SCL,
    .sda                = I2C_SDA,
    .frequency          = NRF_TWI_FREQ_400K,
  };

  err_code = nrf_twi_mngr_init(twi_instance, &twi_config);
  APP_ERROR_CHECK(err_code);
}

void log_init(void)
{
    ret_code_t err_code = NRF_LOG_INIT(NULL);
    APP_ERROR_CHECK(err_code);

    NRF_LOG_DEFAULT_BACKENDS_INIT();
}

void state_step(){
  if (state.take_pic) {
    uint8_t image_buffer[HM01B0_IMAGE_SIZE];
    NRF_LOG_INFO("turning on camera");
    NRF_LOG_INFO("address of buffer: %x", image_buffer);
    NRF_LOG_INFO("size of buffer:    %x", HM01B0_IMAGE_SIZE);


    nrf_gpio_pin_clear(LED_1);
    hm01b0_power_up();

    int error = hm01b0_init_system(sHM01B0InitScript, sizeof(sHM01B0InitScript)/sizeof(hm_script_t));
    NRF_LOG_INFO("error: %d", error);

    hm01b0_blocking_read_oneframe(image_buffer, HM01B0_IMAGE_SIZE);
    nrf_gpio_pin_set(LED_1);
    hm01b0_power_down();
    state.take_pic = false;
  }
}

int main(void) {
    // Initialize.
    nrf_power_dcdcen_set(1);
    log_init();

    nrf_gpio_cfg_output(LED_1);
    nrf_gpio_cfg_output(LED_2);
    nrf_gpio_cfg_output(LED_3);
    nrf_gpio_pin_set(LED_1);
    nrf_gpio_pin_set(LED_2);
    nrf_gpio_pin_set(LED_3);
    for (int i = 0; i < 7; i++) {
      nrf_gpio_cfg_output(enables[i]);
      nrf_gpio_pin_set(enables[i]);
    }

    twi_init(&twi_mngr_instance);

    ret_code_t err_code = app_timer_init();
    APP_ERROR_CHECK(err_code);
    err_code = app_timer_create(&camera_timer, APP_TIMER_MODE_REPEATED, camera_timer_callback);
    APP_ERROR_CHECK(err_code);
    err_code = app_timer_start(camera_timer, SENSOR_PERIOD, NULL);
    APP_ERROR_CHECK(err_code);

    // setup RTC
    ab1815_init(&spi_instance);
    ab1815_control_t ab1815_config;
    ab1815_get_config(&ab1815_config);
    ab1815_config.auto_rst = 1;
    ab1815_set_config(ab1815_config);

    hm01b0_init_if(&twi_mngr_instance);
    hm01b0_mclk_init();
    hm01b0_power_down();

    // setup thread
    thread_config_t thread_config = {
      .channel = 25,
      .panid = 0xFACE,
      .sed = true,
      .poll_period = DEFAULT_POLL_PERIOD,
      .child_period = DEFAULT_CHILD_TIMEOUT,
      .autocommission = true,
    };
    thread_init(&thread_config);

    // Enter main loop.
    while (1) {
        //led_toggle(LED);
        thread_process();
        state_step();
        if (NRF_LOG_PROCESS() == false)
        {
          thread_sleep();
        }
    }
}
