#define COAP_SERVER_HOSTNAME "coap.permamote.com"
#define NTP_SERVER_HOSTNAME "time.nist.gov"
#define DNS_SERVER_ADDR "fdaa:bb:1::2"
#define PARSE_ADDR "j2x.us/perm"

#define DEFAULT_CHILD_TIMEOUT    2*60  /**< Thread child timeout [s]. */
#define DEFAULT_POLL_PERIOD      60000 /**< Thread Sleepy End Device polling period when Asleep. [ms] */
#define RECV_POLL_PERIOD         100   /**< Thread Sleepy End Device polling period when expecting response. [ms] */
#define NUM_SLAAC_ADDRESSES      6     /**< Number of SLAAC addresses. */

#define DISCOVER_PERIOD     APP_TIMER_TICKS(5*60*1000)
#define SENSOR_PERIOD       APP_TIMER_TICKS(10*1000)
#define PIR_BACKOFF_PERIOD  APP_TIMER_TICKS(2*60*1000)
#define PIR_DELAY           APP_TIMER_TICKS(10*1000)
#define RTC_UPDATE_FIRST    APP_TIMER_TICKS(4*1000)
