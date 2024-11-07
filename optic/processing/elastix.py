from __future__ import annotations
from ..type_definitions import *
import numpy as np
import itk
from itk.elxParameterObjectPython import elastixParameterObject


def convertDictToElastixFormat(dict_params: Dict[str, Any]) -> Dict[str, Tuple[str]]:
    return {k: tuple(v) if isinstance(v, list) else (str(v),) for k, v in dict_params.items()}

# calculate transform parameters
def calculateSingleTransform(
    img_fix: np.ndarray[np.uint8, Tuple[int, int]], 
    img_mov: np.ndarray[np.uint8, Tuple[int, int]], 
    dict_params: Dict[str, Any], 
) -> Tuple[np.ndarray[np.uint8, Tuple[int, int]], Any]:
    
    img_fix = np.ascontiguousarray(img_fix)
    img_mov = np.ascontiguousarray(img_mov)
    img_fix = itk.image_view_from_array(img_fix)
    img_mov = itk.image_view_from_array(img_mov)

    parameter_map = convertDictToElastixFormat(dict_params)
    parameter_object = itk.ParameterObject.New()
    parameter_object.AddParameterMap(parameter_map)

    img_res, transform_parameters = itk.elastix_registration_method(img_fix, img_mov, parameter_object=parameter_object, output_directory="")
    return transform_parameters

# apply transform parameters to single image
def applySingleTransform(
    img_mov: np.ndarray[np.uint8, Tuple[int, int]], 
    transform_parameters: elastixParameterObject, 
) -> np.ndarray[np.uint8, Tuple[int, int]]:
    
    img_mov = np.ascontiguousarray(img_mov)
    img_mov = itk.image_view_from_array(img_mov)

    img_res = itk.transformix_filter(img_mov, transform_parameters, output_directory="")
    img_res = itk.array_from_image(img_res)
    return img_res

# calculate transform parameters from image stack
def calculateStackTransform(
    img_stack: np.ndarray[np.uint8, Tuple[int, int, int, int, int]], # XYCZT
    dict_params: Dict[str, Any],
    channel_ref: int,
    idx_ref: int,
    axis: Literal["t", "z"],
    display_iters: int = 10
) -> Dict[str, elastixParameterObject]:
    dict_transform_parameters = {}

    i = 0
    if axis == "t": # register t-axis
        for z in range(img_stack.shape[3]):
            img_fix = img_stack[:, :, channel_ref, z, idx_ref]
            for t in range(img_stack.shape[4]):
                if i % display_iters == 0:
                    print(f"{i} images processed")
                img_mov = img_stack[:, :, channel_ref, z, t]
                transform_parameters = calculateSingleTransform(img_fix, img_mov, dict_params)
                dict_transform_parameters[f"z{z}_t{t}"] = transform_parameters
                i += 1
    elif axis == "z": # register z-axis
        for t in range(img_stack.shape[4]):
            img_fix = img_stack[:, :, channel_ref, idx_ref, t]
            for z in range(img_stack.shape[3]):
                if i % display_iters == 0:
                    print(f"{i} images processed")
                img_mov = img_stack[:, :, channel_ref, z, t]
                transform_parameters = calculateSingleTransform(img_fix, img_mov, dict_params)
                dict_transform_parameters[f"z{z}_t{t}"] = transform_parameters
                i += 1
    print("transform parameters calculation completed")
    return dict_transform_parameters

# apply transform parameters to image stack
def applyStackTransform(
    img_stack: np.ndarray[np.uint8, Tuple[int, int, int, int, int]], # XYCZT
    dict_transform_parameters: Dict[str, elastixParameterObject],
) -> np.ndarray[np.uint8, Tuple[int, int]]:
    img_stack_reg = np.zeros_like(img_stack)
    num_c, num_z, num_t = img_stack.shape[2], img_stack.shape[3], img_stack.shape[4]
    for c in range(num_c):
        for z in range(num_z):
            for t in range(num_t):
                transform_parameters = dict_transform_parameters[f"z{z}_t{t}"]
                img_mov = img_stack[:, :, c, z, t]
                img_res = applySingleTransform(img_mov, transform_parameters)
                img_stack_reg[:, :, c, z, t] = img_res
    print("image transformation completed")
    return img_stack_reg

# run elastix registration for image stack
def runStackRegistration(
    img_stack: np.ndarray[np.uint8, Tuple[int, int, int, int, int]], # XYCZT
    dict_params: Dict[str, Any],
    channel_ref: int,
    idx_ref: int,
    axis: Literal["t", "z"],
    display_iters: int = 10
) -> np.ndarray[np.uint8, Tuple[int, int]]:
    dict_transform_parameters = calculateStackTransform(img_stack, dict_params, channel_ref, idx_ref, axis, display_iters)
    img_stack_reg = applyStackTransform(img_stack, dict_transform_parameters)
    return img_stack_reg
