/* Automatically generated nanopb constant definitions */
/* Generated by nanopb-0.3.9.3 at Sun Nov 10 18:42:17 2019. */

#include "parse.pb.h"

/* @@protoc_insertion_point(includes) */
#if PB_PROTO_HEADER_VERSION != 30
#error Regenerate this file with the current version of nanopb generator.
#endif



const pb_field_t Header_fields[6] = {
    PB_FIELD(  1, UINT32  , SINGULAR, STATIC  , FIRST, Header, version, version, 0),
    PB_FIELD(  2, BYTES   , SINGULAR, STATIC  , OTHER, Header, id, version, 0),
    PB_FIELD(  3, UINT32  , SINGULAR, STATIC  , OTHER, Header, seq_no, id, 0),
    PB_FIELD(  4, UINT64  , SINGULAR, STATIC  , OTHER, Header, tv_sec, seq_no, 0),
    PB_FIELD(  5, UINT32  , SINGULAR, STATIC  , OTHER, Header, tv_usec, tv_sec, 0),
    PB_LAST_FIELD
};

const pb_field_t Data_fields[21] = {
    PB_FIELD(  1, STRING  , SINGULAR, STATIC  , FIRST, Data, discovery, discovery, 0),
    PB_FIELD(  2, STRING  , SINGULAR, STATIC  , OTHER, Data, version, discovery, 0),
    PB_FIELD( 10, FLOAT   , SINGULAR, STATIC  , OTHER, Data, temperature_c, version, 0),
    PB_FIELD( 11, FLOAT   , SINGULAR, STATIC  , OTHER, Data, pressure_mbar, temperature_c, 0),
    PB_FIELD( 12, FLOAT   , SINGULAR, STATIC  , OTHER, Data, humidity_percent, pressure_mbar, 0),
    PB_FIELD( 20, FLOAT   , SINGULAR, STATIC  , OTHER, Data, primary_voltage, humidity_percent, 0),
    PB_FIELD( 21, FLOAT   , SINGULAR, STATIC  , OTHER, Data, solar_voltage, primary_voltage, 0),
    PB_FIELD( 22, FLOAT   , SINGULAR, STATIC  , OTHER, Data, secondary_voltage, solar_voltage, 0),
    PB_FIELD( 23, BOOL    , SINGULAR, STATIC  , OTHER, Data, vbat_ok, secondary_voltage, 0),
    PB_FIELD( 30, FLOAT   , SINGULAR, STATIC  , OTHER, Data, light_color_cct_k, vbat_ok, 0),
    PB_FIELD( 31, UINT32  , SINGULAR, STATIC  , OTHER, Data, light_color_red, light_color_cct_k, 0),
    PB_FIELD( 32, UINT32  , SINGULAR, STATIC  , OTHER, Data, light_color_green, light_color_red, 0),
    PB_FIELD( 33, UINT32  , SINGULAR, STATIC  , OTHER, Data, light_color_blue, light_color_green, 0),
    PB_FIELD( 34, UINT32  , SINGULAR, STATIC  , OTHER, Data, light_color_clear, light_color_blue, 0),
    PB_FIELD( 35, FLOAT   , SINGULAR, STATIC  , OTHER, Data, light_lux, light_color_clear, 0),
    PB_FIELD( 40, BOOL    , SINGULAR, STATIC  , OTHER, Data, motion, light_lux, 0),
    PB_FIELD( 50, UINT32  , SINGULAR, STATIC  , OTHER, Data, thread_rloc16, motion, 0),
    PB_FIELD( 51, BYTES   , SINGULAR, STATIC  , OTHER, Data, thread_ext_addr, thread_rloc16, 0),
    PB_FIELD( 52, UINT32  , SINGULAR, STATIC  , OTHER, Data, thread_parent_avg_rssi, thread_ext_addr, 0),
    PB_FIELD( 53, UINT32  , SINGULAR, STATIC  , OTHER, Data, thread_parent_last_rssi, thread_parent_avg_rssi, 0),
    PB_LAST_FIELD
};

const pb_field_t Message_fields[3] = {
    PB_FIELD(  1, MESSAGE , SINGULAR, STATIC  , FIRST, Message, header, header, &Header_fields),
    PB_FIELD(  2, MESSAGE , SINGULAR, STATIC  , OTHER, Message, data, header, &Data_fields),
    PB_LAST_FIELD
};


/* Check that field information fits in pb_field_t */
#if !defined(PB_FIELD_32BIT)
/* If you get an error here, it means that you need to define PB_FIELD_32BIT
 * compile-time option. You can do that in pb.h or on compiler command line.
 * 
 * The reason you need to do this is that some of your messages contain tag
 * numbers or field sizes that are larger than what can fit in 8 or 16 bit
 * field descriptors.
 */
PB_STATIC_ASSERT((pb_membersize(Message, header) < 65536 && pb_membersize(Message, data) < 65536), YOU_MUST_DEFINE_PB_FIELD_32BIT_FOR_MESSAGES_Header_Data_Message)
#endif

#if !defined(PB_FIELD_16BIT) && !defined(PB_FIELD_32BIT)
/* If you get an error here, it means that you need to define PB_FIELD_16BIT
 * compile-time option. You can do that in pb.h or on compiler command line.
 * 
 * The reason you need to do this is that some of your messages contain tag
 * numbers or field sizes that are larger than what can fit in the default
 * 8 bit descriptors.
 */
PB_STATIC_ASSERT((pb_membersize(Message, header) < 256 && pb_membersize(Message, data) < 256), YOU_MUST_DEFINE_PB_FIELD_16BIT_FOR_MESSAGES_Header_Data_Message)
#endif


/* @@protoc_insertion_point(eof) */
