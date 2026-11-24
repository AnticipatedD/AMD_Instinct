/*
 * Copyright (C) 2020 - 2022 Xilinx, Inc.
 * Copyright (C) 2022-2023 Advanced Micro Devices, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/* Update of this file by the user is not encouraged */
#include <vvas/vvas_kernel.h>
#include <vvas_core/vvas_device.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#ifdef XLNX_PCIe_PLATFORM
#include <xrt.h>
#include <ert.h>
#endif
#include <string.h>
#include <errno.h>
#include <sys/mman.h>

#undef DUMP_REG                 // dump reg_map just before sending ert cmd

static VvasLogLevel log_level = VVAS_LOG_LEVEL_WARNING;

static const char *
vvas_strerror (int errnum, char *errbuf, size_t errbuf_size)
{
#if defined(__GLIBC__) && defined(_GNU_SOURCE)
  return strerror_r (errnum, errbuf, errbuf_size);
#else
  if (strerror_r (errnum, errbuf, errbuf_size) == 0)
    return errbuf;

  snprintf (errbuf, errbuf_size, "errno %d", errnum);
  return errbuf;
#endif
}

VVASFrame *
vvas_alloc_buffer (VVASKernel *handle, uint32_t size, VVASMemoryType mem_type,
    uint16_t mem_bank, VVASFrameProps *props)
{
  VVASFrame *frame = NULL;
  xrt_buffer buffer;
  VvasReturnType vret;

  if (!handle) {
    VVAS_LOG_ERROR (log_level, "invalid arguments : handle %p", handle);
    goto error;
  }

  frame = (VVASFrame *) calloc (1, sizeof (VVASFrame));
  if (!frame) {
    VVAS_LOG_ERROR (log_level, "failed to allocate vvas_frame");
    goto error;
  }
  frame->mem_type = mem_type;

  if (mem_type == VVAS_INTERNAL_MEMORY) {
    frame->size[0] = size;
    vret = vvas_xrt_alloc_xrt_buffer (handle->dev_handle,
        size, VVAS_BO_FLAGS_NONE, mem_bank, &buffer);
    if (VVAS_IS_ERROR (vret)) {
      VVAS_LOG_ERROR (log_level, "failed to allocate internal memory");
      goto error;
    }
    frame->bo[0] = buffer.bo;
    frame->vaddr[0] = buffer.user_ptr;
    frame->paddr[0] = buffer.phy_addr;
    frame->meta_data = NULL;
    frame->app_priv = NULL;
    frame->n_planes = 1;
  } else {
    if (!props || !props->width || !props->height
        || (props->fmt == VVAS_VMFT_UNKNOWN)) {
      VVAS_LOG_ERROR (log_level, "invalid arguments for properties");
      goto error;
    }

    memcpy (&(frame->props), props, sizeof (VVASFrameProps));
    if (!handle->alloc_func) {
      VVAS_LOG_ERROR (log_level,
          "app did not set alloc_func callback function");
      goto error;
    }

    vret = handle->alloc_func (handle, frame, mem_bank, handle->cb_user_data);
    if (VVAS_IS_ERROR (vret)) {
      VVAS_LOG_ERROR (log_level, "failed to allocate frame memory");
      goto error;
    }
  }
  return frame;

error:
  if (frame) {
    vvas_free_buffer (handle, frame);
  }
  return NULL;
}

void
vvas_free_buffer (VVASKernel *handle, VVASFrame *vvas_frame)
{
  xrt_buffer buffer;

  if (!vvas_frame) {
    VVAS_LOG_ERROR (log_level, "invalid arguments : vvas_frame  %p",
        vvas_frame);
    return;
  }

  if (vvas_frame->mem_type == VVAS_INTERNAL_MEMORY) {
    buffer.user_ptr = vvas_frame->vaddr[0];
    buffer.bo = vvas_frame->bo[0];
    buffer.size = vvas_frame->size[0];
    vvas_xrt_free_xrt_buffer (&buffer);
  } else if (handle) {
    if (!handle->free_func) {
      VVAS_LOG_ERROR (log_level, "app did not set free_func callback function");
    } else {
      handle->free_func (handle, vvas_frame, handle->cb_user_data);
    }
  }
  free (vvas_frame);
}

VvasReturnType
vvas_kernel_start (VVASKernel *handle, const char *format, ...)
{
  va_list args;
  VvasReturnType vret;

  if (!handle) {
    VVAS_LOG_ERROR (log_level, "invalid arguments : handle %p", handle);
    return VVAS_RET_ERROR;
  }

  if (!format) {
    VVAS_LOG_ERROR (log_level, "invalid arguments : format %p", format);
    return VVAS_RET_ERROR;
  }

  va_start (args, format);

  vret = vvas_xrt_exec_buf (handle->dev_handle, handle->kern_handle,
      &handle->run_handle, format, args);
  if (VVAS_IS_ERROR (vret)) {
    VVAS_LOG_ERROR (log_level, "failed to issue XRT command");
    va_end (args);
    return vret;
  }
  VVAS_LOG_DEBUG (log_level, "Submitted command to kernel");
  va_end (args);

  return VVAS_RET_SUCCESS;
}

VvasReturnType
vvas_kernel_done (VVASKernel *handle, int32_t timeout)
{
  int ret;
  int retry_count = MAX_EXEC_WAIT_RETRY_CNT;

  if (!handle) {
    VVAS_LOG_ERROR (log_level, "invalid arguments : handle %p", handle);
    return VVAS_RET_ERROR;
  }

  VVAS_LOG_DEBUG (log_level,
      "kernel:%s> Going to wait for kernel command to finish", handle->name);

  do {
    ret = vvas_xrt_exec_wait (handle->dev_handle, handle->run_handle, timeout);
    if (ret == ERT_CMD_STATE_TIMEOUT) {
      VVAS_LOG_WARNING (log_level, "kernel=%s : Timeout...retry execwait",
          handle->name);
      if (retry_count-- <= 0) {
        VVAS_LOG_ERROR (log_level,
            "kernel:%s> Max retry count %d reached..returning error",
            handle->name, MAX_EXEC_WAIT_RETRY_CNT);
        vvas_xrt_free_run_handle (handle->run_handle);
        return VVAS_RET_ERROR;
      }
    } else if (ret == ERT_CMD_STATE_ERROR) {
      VVAS_LOG_ERROR (log_level, "kernel:%s> ExecWait ret = %d", handle->name,
          ret);
      vvas_xrt_free_run_handle (handle->run_handle);
      return VVAS_RET_ERROR;
    }
  } while (ret != ERT_CMD_STATE_COMPLETED);

  vvas_xrt_free_run_handle (handle->run_handle);

  VVAS_LOG_DEBUG (log_level,
      "kernel:%s> Successfully completed kernel command", handle->name);

  return VVAS_RET_SUCCESS;
}

VvasReturnType
vvas_sync_data (VVASKernel *handle, VVASSyncDataFlag flag, VVASFrame *frame)
{
  int plane_id;
  VvasReturnType vret;
  int errnum = 0;
  char errbuf[128];

  vvas_bo_sync_direction sync_flag =
      (flag ==
      VVAS_SYNC_DATA_TO_DEVICE) ? VVAS_BO_SYNC_BO_TO_DEVICE :
      VVAS_BO_SYNC_BO_FROM_DEVICE;

  for (plane_id = 0; plane_id < frame->n_planes; plane_id++) {
    VVAS_LOG_DEBUG (log_level, "plane %d syncing %s : bo = %p, size = %d",
        plane_id,
        sync_flag == VVAS_BO_SYNC_BO_TO_DEVICE ? "to device" : "from device",
        frame->bo[plane_id], frame->size[plane_id]);

    vret =
        vvas_xrt_sync_bo (frame->bo[plane_id], sync_flag,
        frame->size[plane_id], 0);
    if (VVAS_IS_ERROR (vret)) {
      errnum = errno;
      VVAS_LOG_ERROR (log_level, "vvas_xrt_sync_bo failed %d, reason : %s",
          vret, vvas_strerror (errnum, errbuf, sizeof (errbuf)));
      return vret;
    }
  }
  return VVAS_RET_SUCCESS;
}

/***************** vvas caps utils ********************/
bool
vvas_caps_set_pad_nature (VVASKernel *handle, padsnature nature)
{
  if (!handle->padinfo)
    handle->padinfo = (vvaspads *) calloc (1, sizeof (vvaspads));
  if (handle->padinfo) {
    handle->padinfo->nature = nature;
  } else
    return false;
  return true;
}

size_t
vvas_kernel_get_batch_size (VVASKernel *handle)
{
  return handle->kernel_batch_sz;
}

padsnature
vvas_caps_get_pad_nature (VVASKernel *handle)
{
  if (!handle->padinfo)
    return VVAS_PAD_DEFAULT;
  else
    return handle->padinfo->nature;
}

bool
vvas_caps_set_stride_align (VVASKernel *handle, paddir dir,
    unsigned int stride_align)
{
  if (!handle->padinfo)
    handle->padinfo = (vvaspads *) calloc (1, sizeof (vvaspads));
  if (handle->padinfo) {
    if (dir == SINK)
      handle->padinfo->sinkpad_align.stride_align = stride_align;
    else
      handle->padinfo->srcpad_align.stride_align = stride_align;
  } else
    return false;
  return true;
}

bool
vvas_caps_set_sink_stride_align (VVASKernel *handle, unsigned int stride_align)
{
  return vvas_caps_set_stride_align (handle, SINK, stride_align);
}

bool
vvas_caps_set_src_stride_align (VVASKernel *handle, unsigned int stride_align)
{
  return vvas_caps_set_stride_align (handle, SRC, stride_align);
}

unsigned int
vvas_caps_get_stride_align (VVASKernel *handle, paddir dir)
{
  if (!handle->padinfo)
    return 1;
  else {
    if (dir == SINK)
      return handle->padinfo->sinkpad_align.stride_align ? handle->padinfo->
          sinkpad_align.stride_align : 1;
    else
      return handle->padinfo->srcpad_align.stride_align ? handle->padinfo->
          srcpad_align.stride_align : 1;
  }
}

unsigned int
vvas_caps_get_sink_stride_align (VVASKernel *handle)
{
  return vvas_caps_get_stride_align (handle, SINK);
}

unsigned int
vvas_caps_get_src_stride_align (VVASKernel *handle)
{
  return vvas_caps_get_stride_align (handle, SRC);
}

bool
vvas_caps_set_height_align (VVASKernel *handle, paddir dir,
    unsigned int height_align)
{
  if (!handle->padinfo)
    handle->padinfo = (vvaspads *) calloc (1, sizeof (vvaspads));
  if (handle->padinfo) {
    if (dir == SINK)
      handle->padinfo->sinkpad_align.height_align = height_align;
    else
      handle->padinfo->srcpad_align.height_align = height_align;
  } else
    return false;
  return true;
}

bool
vvas_caps_set_sink_height_align (VVASKernel *handle, unsigned int height_align)
{
  return vvas_caps_set_height_align (handle, SINK, height_align);
}

bool
vvas_caps_set_src_height_align (VVASKernel *handle, unsigned int height_align)
{
  return vvas_caps_set_height_align (handle, SRC, height_align);
}

unsigned int
vvas_caps_get_height_align (VVASKernel *handle, paddir dir)
{
  if (!handle->padinfo)
    return 1;
  else {
    if (dir == SINK)
      return handle->padinfo->sinkpad_align.height_align ? handle->padinfo->
          sinkpad_align.height_align : 1;
    else
      return handle->padinfo->srcpad_align.height_align ? handle->padinfo->
          srcpad_align.height_align : 1;
  }
}

unsigned int
vvas_caps_get_sink_height_align (VVASKernel *handle)
{
  return vvas_caps_get_height_align (handle, SINK);
}

unsigned int
vvas_caps_get_src_height_align (VVASKernel *handle)
{
  return vvas_caps_get_height_align (handle, SRC);
}

/**
 * vvas_caps_new() - Create new caps with input parameters
 * range_height
 * 	- true  : if kernel support range of height
 * 	- false : if kernel support fixed height
 * lower_height : lower value of height supported by kernel
 *                if range_height is false, this holds the fixed value
 * upper_height : higher value of hight supported by kernel
 *                if range_height is false, this should be 0
 *
 * range_width : same as above
 * lower_width :
 * upper_width :
 *
 * ...         : variable range of format supported terminated by 0
 *               make sure to add 0 at end otherwise it
 *               code will take format till it get 0
 *
 */

kernelcaps *
vvas_caps_new (uint8_t range_height, uint32_t lower_height,
    uint32_t upper_height, uint8_t range_width, uint32_t lower_width,
    uint32_t upper_width, ...)
{

  va_list valist;
  int i, num_fmt = 0;
  kernelcaps *kcaps;

  if (lower_height == 0 && lower_width == 0) {
    VVAS_LOG_ERROR (log_level,
        "Wrong parameter lower_width = %d, lower_width = %d\n", lower_height,
        lower_width);
    return NULL;
  }

  if ((range_height == true && (upper_height == 0 || lower_height == 0)) &&
      (range_width == true && (upper_width == 0 || lower_width == 0)) &&
      (lower_height == 0 && lower_width == 0)) {

    VVAS_LOG_ERROR (log_level, "vvas_caps_new: Wrong parameters:");
    VVAS_LOG_ERROR (log_level,
        "range_height = %d, lower_height = %d upper_height = %d, ",
        range_height, lower_height, upper_height);
    VVAS_LOG_ERROR (log_level,
        "range_width = %d, lower_width = %d upper_width = %d, ", range_height,
        lower_height, upper_height);
    return NULL;
  }

  kcaps = (kernelcaps *) calloc (1, sizeof (kernelcaps));

  kcaps->range_height = range_height;
  kcaps->lower_height = lower_height;
  kcaps->upper_height = upper_height;
  kcaps->range_width = range_width;
  kcaps->lower_width = lower_width;
  kcaps->upper_width = upper_width;

  va_start (valist, upper_width);
  while (va_arg (valist, int) != 0)
      num_fmt++;
  va_end (valist);

  if (!num_fmt) {
    VVAS_LOG_ERROR (log_level, "vvas_caps_new: No format provided\n");
    free (kcaps);
    return NULL;
  }

  kcaps->fmt = (VVASVideoFormat *) calloc (num_fmt, sizeof (VVASVideoFormat));
  kcaps->num_fmt = num_fmt;

  va_start (valist, upper_width);
  for (i = 0; i < num_fmt; i++) {
    kcaps->fmt[i] = va_arg (valist, int);
  }
  va_end (valist);

  return kcaps;
}

bool
vvas_caps_add (VVASKernel *handle, kernelcaps *kcaps, paddir dir,
    int sinkpad_num)
{
  kernelpads **pads;

  if (sinkpad_num != 0) {
    VVAS_LOG_ERROR (log_level,
        "vvas_caps_add_to_sink: only one pad supported yet\n");
    return false;
  }

  if (!handle->padinfo) {
    bool ret;
    ret = vvas_caps_set_pad_nature (handle, VVAS_PAD_DEFAULT);
    if (!ret) {
      VVAS_LOG_ERROR (log_level, "vvas_caps_add: failed to set pad nature\n");
      return false;
    }
  }

  if (dir == SINK) {
    if (!handle->padinfo->sinkpads)
      handle->padinfo->sinkpads =
          (kernelpads **) calloc (1, sizeof (kernelpads *));

    pads = handle->padinfo->sinkpads;
  } else {
    if (!handle->padinfo->srcpads)
      handle->padinfo->srcpads =
          (kernelpads **) calloc (1, sizeof (kernelpads *));

    pads = handle->padinfo->srcpads;
  }

  if (!pads[sinkpad_num]) {
    pads[sinkpad_num] = (kernelpads *) calloc (1, sizeof (kernelpads));
    handle->padinfo->nu_sinkpad++;
  }

  pads[sinkpad_num]->kcaps =
      (kernelcaps **) realloc (pads[sinkpad_num]->kcaps,
      (pads[sinkpad_num]->nu_caps + 1) * sizeof (kernelcaps *));
  pads[sinkpad_num]->kcaps[pads[sinkpad_num]->nu_caps] = kcaps;

  pads[sinkpad_num]->nu_caps++;

  return true;
}

/**
 * vvas_caps_add_to_sink() - add new caps created by vvas_caps_new() to sink
 *                          these caps are used by xfilter to negosiate 
 *                          with upstream plugin
 *                          Only one pad is supported yet
 */
bool
vvas_caps_add_to_sink (VVASKernel *handle, kernelcaps *kcaps, int sinkpad_num)
{
  return vvas_caps_add (handle, kcaps, 0, sinkpad_num);
}

/**
 * vvas_caps_add_to_sink() - add new caps created by vvas_caps_new() to src
 *                          these caps are used by xfilter to negosiate 
 *                          with downstream plugin
 *                          Only one pad is supported yet
 */
bool
vvas_caps_add_to_src (VVASKernel *handle, kernelcaps *kcaps, int srcpad_num)
{
  return vvas_caps_add (handle, kcaps, 1, srcpad_num);
}

int
vvas_caps_get_num_caps (VVASKernel *handle, int sinkpad_num)
{
  if ((handle->padinfo) && (handle->padinfo->sinkpads[sinkpad_num]))
    return handle->padinfo->sinkpads[sinkpad_num]->nu_caps;
  else
    return 0;
}

int
vvas_caps_get_num_sinkpads (VVASKernel *handle)
{
  if (handle->padinfo)
    return handle->padinfo->nu_sinkpad;
  else
    return 0;
}

int
vvas_caps_get_num_srcpads (VVASKernel *handle)
{
  if (handle->padinfo)
    return handle->padinfo->nu_srcpad;
  else
    return 0;
}

void
vvas_caps_free (VVASKernel *handle)
{
  int i, j;
  kernelpads **pads;

  if (!handle || !handle->padinfo)
    return;

  pads = handle->padinfo->sinkpads;
  if (pads) {
    for (i = 0; i < handle->padinfo->nu_sinkpad; i++) {
      for (j = 0; j < pads[i]->nu_caps; j++) {
        free (pads[i]->kcaps[j]->fmt);
        free (pads[i]->kcaps[j]);
      }
      free (pads[i]->kcaps);
      free (pads[i]);
    }
    free (pads);
  }

  pads = handle->padinfo->srcpads;
  if (pads) {
    for (i = 0; i < handle->padinfo->nu_sinkpad; i++) {
      for (j = 0; j < pads[i]->nu_caps; j++) {
        free (pads[i]->kcaps[j]->fmt);
        free (pads[i]->kcaps[j]);
      }
      free (pads[i]->kcaps);
      free (pads[i]);
    }
    free (pads);
  }

  free (handle->padinfo);
}

void
vvas_caps_print (VVASKernel *handle)
{
  int i, j, k;
  kernelpads **pads;
  if (!handle || !handle->padinfo)
    return;

  pads = handle->padinfo->sinkpads;
  VVAS_LOG_DEBUG (log_level, "total sinkpad %d", handle->padinfo->nu_sinkpad);
  if (pads) {
    for (i = 0; i < handle->padinfo->nu_sinkpad; i++) {
      VVAS_LOG_DEBUG (log_level, "nu of caps for sinkpad[%d] = %d", i,
          pads[i]->nu_caps);
      VVAS_LOG_DEBUG (log_level, "value are");
      VVAS_LOG_DEBUG (log_level,
          "range_height\tlower_height\tupper_height\trange_width\tlower_width\tupper_width\tfmt...");
      for (j = 0; j < pads[i]->nu_caps; j++) {

        VVAS_LOG_DEBUG (log_level, "%d\t\t%d\t\t%d\t\t%d\t\t%d\t\t%d\t\t ",
            pads[i]->kcaps[j]->range_height, pads[i]->kcaps[j]->lower_height,
            pads[i]->kcaps[j]->upper_height, pads[i]->kcaps[j]->range_width,
            pads[i]->kcaps[j]->lower_width, pads[i]->kcaps[j]->upper_width);
        for (k = 0; k < pads[i]->kcaps[j]->num_fmt; k++)
          VVAS_LOG_DEBUG (log_level, "%d ", pads[i]->kcaps[j]->fmt[k]);
      }
    }
  }

  pads = handle->padinfo->srcpads;
  VVAS_LOG_DEBUG (log_level, "total srcpad %d", handle->padinfo->nu_srcpad);
  if (pads) {
    for (i = 0; i < handle->padinfo->nu_srcpad; i++) {
      VVAS_LOG_DEBUG (log_level, "nu of caps for srcpad[%d] = %d", i,
          pads[i]->nu_caps);
      VVAS_LOG_DEBUG (log_level, "value are");
      VVAS_LOG_DEBUG (log_level,
          "range_height\tlower_height\tupper_height\trange_width\tlower_width\tupper_width\tfmt...");
      for (j = 0; j < pads[i]->nu_caps; j++) {

        VVAS_LOG_DEBUG (log_level, "%d\t\t%d\t\t%d\t\t%d\t\t%d\t\t%d\t\t ",
            pads[i]->kcaps[j]->range_height, pads[i]->kcaps[j]->lower_height,
            pads[i]->kcaps[j]->upper_height, pads[i]->kcaps[j]->range_width,
            pads[i]->kcaps[j]->lower_width, pads[i]->kcaps[j]->upper_width);
        for (k = 0; k < pads[i]->kcaps[j]->num_fmt; k++)
          VVAS_LOG_DEBUG (log_level, "%d ", pads[i]->kcaps[j]->fmt[k]);
      }
    }
  }
}
