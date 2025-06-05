#include "gif_delta_reader.h"
#include <stdlib.h>
#include <string.h>

/* Internal helper functions */
static char* read_string(FILE* file) {
    uint32_t length;
    if (fread(&length, sizeof(uint32_t), 1, file) != 1) {
        return NULL;
    }
    
    if (length == 0) {
        char* empty_str = malloc(1);
        if (empty_str) empty_str[0] = '\0';
        return empty_str;
    }
    
    char* str = malloc(length + 1);
    if (!str) return NULL;
    
    if (fread(str, 1, length, file) != length) {
        free(str);
        return NULL;
    }
    
    str[length] = '\0';
    return str;
}

static int read_frame(FILE* file, gifd_frame_t* frame) {
    /* Read frame index */
    if (fread(&frame->frame_index, sizeof(uint32_t), 1, file) != 1) {
        return 0;
    }
    
    /* Read frame type */
    uint8_t type_byte;
    if (fread(&type_byte, sizeof(uint8_t), 1, file) != 1) {
        return 0;
    }
    frame->type = (gifd_frame_type_t)type_byte;
    
    /* Read duration */
    if (fread(&frame->duration, sizeof(uint32_t), 1, file) != 1) {
        return 0;
    }
    
    /* Read bounding box */
    if (fread(&frame->bounding_box, sizeof(gifd_bbox_t), 1, file) != 1) {
        return 0;
    }
    
    /* Initialize pointers */
    frame->reference_filename = NULL;
    frame->delta_boxes = NULL;
    frame->delta_box_count = 0;
    
    if (frame->type == GIFD_FRAME_REFERENCE) {
        /* Read reference filename */
        frame->reference_filename = read_string(file);
        if (!frame->reference_filename) {
            return 0;
        }
        
        /* Read delta box count (should be 0 for reference frames) */
        if (fread(&frame->delta_box_count, sizeof(uint32_t), 1, file) != 1) {
            free(frame->reference_filename);
            frame->reference_filename = NULL;
            return 0;
        }
    } else {
        /* Read delta box count */
        if (fread(&frame->delta_box_count, sizeof(uint32_t), 1, file) != 1) {
            return 0;
        }
        
        /* Allocate and read delta boxes */
        if (frame->delta_box_count > 0) {
            frame->delta_boxes = malloc(frame->delta_box_count * sizeof(gifd_delta_box_t));
            if (!frame->delta_boxes) {
                return 0;
            }
            
            for (uint32_t i = 0; i < frame->delta_box_count; i++) {
                gifd_delta_box_t* box = &frame->delta_boxes[i];
                
                /* Read filename */
                box->filename = read_string(file);
                if (!box->filename) {
                    /* Free previously allocated strings */
                    for (uint32_t j = 0; j < i; j++) {
                        free(frame->delta_boxes[j].filename);
                    }
                    free(frame->delta_boxes);
                    frame->delta_boxes = NULL;
                    return 0;
                }
                
                /* Read bounding box */
                if (fread(&box->bounding_box, sizeof(gifd_bbox_t), 1, file) != 1) {
                    for (uint32_t j = 0; j <= i; j++) {
                        free(frame->delta_boxes[j].filename);
                    }
                    free(frame->delta_boxes);
                    frame->delta_boxes = NULL;
                    return 0;
                }
                
                /* Read position */
                if (fread(&box->position, sizeof(gifd_position_t), 1, file) != 1) {
                    for (uint32_t j = 0; j <= i; j++) {
                        free(frame->delta_boxes[j].filename);
                    }
                    free(frame->delta_boxes);
                    frame->delta_boxes = NULL;
                    return 0;
                }
                
                /* Read size */
                if (fread(&box->size, sizeof(gifd_size_t), 1, file) != 1) {
                    for (uint32_t j = 0; j <= i; j++) {
                        free(frame->delta_boxes[j].filename);
                    }
                    free(frame->delta_boxes);
                    frame->delta_boxes = NULL;
                    return 0;
                }
            }
        }
    }
    
    return 1;
}

/* Public API functions */

gifd_data_t* gifd_load_from_file(const char* filename) {
    FILE* file = fopen(filename, "rb");
    if (!file) {
        return NULL;
    }
    
    gifd_data_t* data = malloc(sizeof(gifd_data_t));
    if (!data) {
        fclose(file);
        return NULL;
    }
    
    /* Initialize pointers */
    data->original_filename = NULL;
    data->frames = NULL;
    
    /* Read header */
    if (fread(&data->magic_number, sizeof(uint32_t), 1, file) != 1 ||
        data->magic_number != GIFD_MAGIC_NUMBER) {
        free(data);
        fclose(file);
        return NULL;
    }
    
    if (fread(&data->format_version, sizeof(uint32_t), 1, file) != 1 ||
        data->format_version != GIFD_FORMAT_VERSION) {
        free(data);
        fclose(file);
        return NULL;
    }
    
    if (fread(&data->width, sizeof(uint32_t), 1, file) != 1 ||
        fread(&data->height, sizeof(uint32_t), 1, file) != 1 ||
        fread(&data->frame_count, sizeof(uint32_t), 1, file) != 1) {
        free(data);
        fclose(file);
        return NULL;
    }
    
    /* Read original filename */
    data->original_filename = read_string(file);
    if (!data->original_filename) {
        free(data);
        fclose(file);
        return NULL;
    }
    
    /* Allocate frames array */
    if (data->frame_count > 0) {
        data->frames = malloc(data->frame_count * sizeof(gifd_frame_t));
        if (!data->frames) {
            free(data->original_filename);
            free(data);
            fclose(file);
            return NULL;
        }
        
        /* Read each frame */
        for (uint32_t i = 0; i < data->frame_count; i++) {
            if (!read_frame(file, &data->frames[i])) {
                /* Free previously loaded frames */
                for (uint32_t j = 0; j < i; j++) {
                    gifd_frame_t* frame = &data->frames[j];
                    if (frame->reference_filename) {
                        free(frame->reference_filename);
                    }
                    if (frame->delta_boxes) {
                        for (uint32_t k = 0; k < frame->delta_box_count; k++) {
                            free(frame->delta_boxes[k].filename);
                        }
                        free(frame->delta_boxes);
                    }
                }
                free(data->frames);
                free(data->original_filename);
                free(data);
                fclose(file);
                return NULL;
            }
        }
    }
    
    fclose(file);
    return data;
}

void gifd_free(gifd_data_t* data) {
    if (!data) return;
    
    if (data->original_filename) {
        free(data->original_filename);
    }
    
    if (data->frames) {
        for (uint32_t i = 0; i < data->frame_count; i++) {
            gifd_frame_t* frame = &data->frames[i];
            
            if (frame->reference_filename) {
                free(frame->reference_filename);
            }
            
            if (frame->delta_boxes) {
                for (uint32_t j = 0; j < frame->delta_box_count; j++) {
                    free(frame->delta_boxes[j].filename);
                }
                free(frame->delta_boxes);
            }
        }
        free(data->frames);
    }
    
    free(data);
}

gifd_frame_t* gifd_get_frame(gifd_data_t* data, uint32_t frame_index) {
    if (!data || frame_index >= data->frame_count) {
        return NULL;
    }
    return &data->frames[frame_index];
}

void gifd_print_info(gifd_data_t* data) {
    if (!data) {
        printf("Error: NULL data pointer\n");
        return;
    }
    
    printf("GIF Delta File Information:\n");
    printf("  Magic Number: 0x%08X\n", data->magic_number);
    printf("  Format Version: %u\n", data->format_version);
    printf("  Dimensions: %u x %u\n", data->width, data->height);
    printf("  Frame Count: %u\n", data->frame_count);
    printf("  Original File: %s\n", data->original_filename ? data->original_filename : "(none)");
    
    printf("\nFrames:\n");
    for (uint32_t i = 0; i < data->frame_count; i++) {
        gifd_frame_t* frame = &data->frames[i];
        printf("  Frame %u:\n", frame->frame_index);
        printf("    Type: %s\n", frame->type == GIFD_FRAME_REFERENCE ? "Reference" : "Multi-Delta");
        printf("    Duration: %u ms\n", frame->duration);
        printf("    Bounding Box: (%u, %u) to (%u, %u)\n", 
               frame->bounding_box.x1, frame->bounding_box.y1,
               frame->bounding_box.x2, frame->bounding_box.y2);
        
        if (frame->type == GIFD_FRAME_REFERENCE) {
            printf("    Reference File: %s\n", frame->reference_filename ? frame->reference_filename : "(none)");
        } else {
            printf("    Delta Boxes: %u\n", frame->delta_box_count);
            for (uint32_t j = 0; j < frame->delta_box_count; j++) {
                gifd_delta_box_t* box = &frame->delta_boxes[j];
                printf("      Box %u: %s\n", j, box->filename ? box->filename : "(none)");
                printf("        Bounds: (%u, %u) to (%u, %u)\n",
                       box->bounding_box.x1, box->bounding_box.y1,
                       box->bounding_box.x2, box->bounding_box.y2);
                printf("        Position: (%u, %u)\n", box->position.x, box->position.y);
                printf("        Size: %u x %u\n", box->size.width, box->size.height);
            }
        }
        printf("\n");
    }
}

int gifd_validate_file(const char* filename) {
    FILE* file = fopen(filename, "rb");
    if (!file) {
        return 0;
    }
    
    uint32_t magic, version;
    if (fread(&magic, sizeof(uint32_t), 1, file) != 1 ||
        fread(&version, sizeof(uint32_t), 1, file) != 1) {
        fclose(file);
        return 0;
    }
    
    fclose(file);
    return (magic == GIFD_MAGIC_NUMBER && version == GIFD_FORMAT_VERSION);
} 