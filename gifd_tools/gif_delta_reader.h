#ifndef GIF_DELTA_READER_H
#define GIF_DELTA_READER_H

#include <stdint.h>
#include <stdio.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Magic number for GIFD format: "GIFD" */
#define GIFD_MAGIC_NUMBER 0x44464947

/* Current format version */
#define GIFD_FORMAT_VERSION 1

/* Frame types */
typedef enum {
    GIFD_FRAME_REFERENCE = 0,
    GIFD_FRAME_MULTI_DELTA = 1
} gifd_frame_type_t;

/* Bounding box structure */
typedef struct {
    uint32_t x1, y1, x2, y2;
} gifd_bbox_t;

/* Position structure */
typedef struct {
    uint32_t x, y;
} gifd_position_t;

/* Size structure */
typedef struct {
    uint32_t width, height;
} gifd_size_t;

/* Delta box structure */
typedef struct {
    char* filename;
    gifd_bbox_t bounding_box;
    gifd_position_t position;
    gifd_size_t size;
} gifd_delta_box_t;

/* Frame structure */
typedef struct {
    uint32_t frame_index;
    gifd_frame_type_t type;
    uint32_t duration;
    gifd_bbox_t bounding_box;
    
    /* For reference frames */
    char* reference_filename;
    
    /* For delta frames */
    uint32_t delta_box_count;
    gifd_delta_box_t* delta_boxes;
} gifd_frame_t;

/* Main GIF delta data structure */
typedef struct {
    uint32_t magic_number;
    uint32_t format_version;
    uint32_t width;
    uint32_t height;
    uint32_t frame_count;
    char* original_filename;
    gifd_frame_t* frames;
} gifd_data_t;

/* Function declarations */

/**
 * Load GIF delta data from a binary file
 * @param filename Path to the .gifd file
 * @return Pointer to loaded data structure, or NULL on error
 */
gifd_data_t* gifd_load_from_file(const char* filename);

/**
 * Free memory allocated for GIF delta data
 * @param data Pointer to the data structure to free
 */
void gifd_free(gifd_data_t* data);

/**
 * Get a specific frame by index
 * @param data Pointer to the GIF delta data
 * @param frame_index Index of the frame to retrieve
 * @return Pointer to the frame, or NULL if index is invalid
 */
gifd_frame_t* gifd_get_frame(gifd_data_t* data, uint32_t frame_index);

/**
 * Print debug information about the loaded data
 * @param data Pointer to the GIF delta data
 */
void gifd_print_info(gifd_data_t* data);

/**
 * Validate that a file has the correct magic number and version
 * @param filename Path to the file to validate
 * @return 1 if valid, 0 if invalid
 */
int gifd_validate_file(const char* filename);

#ifdef __cplusplus
}
#endif

#endif /* GIF_DELTA_READER_H */ 