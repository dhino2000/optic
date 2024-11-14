from __future__ import annotations
from ..type_definitions import *
import os
import numpy as np
import itk
from itk.elxParameterObjectPython import elastixParameterObject
from itk.itkElastixRegistrationMethodPython import elastix_registration_method
from itk.itkTransformixFilterPython import transformix_filter

def convertDictToElastixFormat(dict_params: Dict[str, Any]) -> Dict[str, Tuple[str]]:
    return {k: tuple(v) if isinstance(v, list) else (str(v),) for k, v in dict_params.items()}

# calculate transform parameters
def calculateSingleTransform(
    img_fix: np.ndarray[np.uint8, Tuple[int, int]], 
    img_mov: np.ndarray[np.uint8, Tuple[int, int]], 
    dict_params: Dict[str, Any], 
) -> elastixParameterObject:
    
    img_fix = np.ascontiguousarray(img_fix)
    img_mov = np.ascontiguousarray(img_mov)
    img_fix = itk.image_view_from_array(img_fix)
    img_mov = itk.image_view_from_array(img_mov)

    parameter_map = convertDictToElastixFormat(dict_params)
    parameter_object = elastixParameterObject.New()
    parameter_object.AddParameterMap(parameter_map)

    img_res, transform_parameters = elastix_registration_method(img_fix, img_mov, parameter_object=parameter_object, output_directory="")
    return transform_parameters

# apply transform parameters to single image
def applySingleTransform(
    img_mov: np.ndarray[np.uint8, Tuple[int, int]], 
    transform_parameters: elastixParameterObject, 
) -> np.ndarray[np.uint8, Tuple[int, int]]:
    
    img_mov = np.ascontiguousarray(img_mov)
    img_mov = itk.image_view_from_array(img_mov)

    img_res = transformix_filter(img_mov, transform_parameters, output_directory="")
    img_res = itk.array_from_image(img_res)
    return img_res

# run elastix registration for single image
def runSingleRegistration(
    img_fix: np.ndarray[np.uint8, Tuple[int, int]], 
    img_mov: np.ndarray[np.uint8, Tuple[int, int]], 
    dict_params: Dict[str, Any],
) -> np.ndarray[np.uint8, Tuple[int, int]]:
    transform_parameters = calculateStackTransform(img_fix, img_mov, dict_params)
    img_reg = applyStackTransform(img_mov, transform_parameters)
    return img_reg

# calculate transform parameters from image stack
def calculateStackTransform(
    img_stack: np.ndarray[np.uint8, Tuple[int, int, int, int, int]], # XYCZT
    dict_params: Dict[str, Any],
    channel_ref: int,
    idx_ref: int,
    axis: Literal["t", "z"],
) -> Dict[str, elastixParameterObject]:
    dict_transform_parameters = {}

    if axis == "t": # register t-axis
        for z in range(img_stack.shape[3]):
            img_fix = img_stack[:, :, channel_ref, z, idx_ref]
            for t in range(img_stack.shape[4]):
                img_mov = img_stack[:, :, channel_ref, z, t]
                transform_parameters = calculateSingleTransform(img_fix, img_mov, dict_params)
                dict_transform_parameters[f"z{z}_t{t}"] = transform_parameters
                print("calculating", "z:", z, "t:", t)
    elif axis == "z": # register z-axis
        for t in range(img_stack.shape[4]):
            img_fix = img_stack[:, :, channel_ref, idx_ref, t]
            for z in range(img_stack.shape[3]):
                img_mov = img_stack[:, :, channel_ref, z, t]
                transform_parameters = calculateSingleTransform(img_fix, img_mov, dict_params)
                dict_transform_parameters[f"z{z}_t{t}"] = transform_parameters
                print("calculating", "z:", z, "t:", t)
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
                print("applying", "c", c, "z:", z, "t:", t)
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

# generate point's coordination file for elastix registration
def generateTmpTextforRegistration(coords: np.ndarray[np.uint8, Tuple[int, int]], path_dst: str):
    np.savetxt(path_dst, coords, fmt = "%.5f")
    # Modify the file
    with open(path_dst, 'r') as f:
        l = f.readlines()

    l.insert(0, 'point\n')
    l.insert(1, f'{len(coords)}\n')

    with open(path_dst, 'w') as f:
        f.writelines(l)

# apply transform parameters to points
def applyPointTransform(
    img_mov: np.ndarray[np.uint8, Tuple[int, int]], 
    transform_parameters: elastixParameterObject, 
    points: np.ndarray[np.int32, Tuple[int, int]],
    path_txt: str= "./points_tmp.txt",

) -> np.ndarray[np.int32, Tuple[int, int]]:
    
    img_mov = np.ascontiguousarray(img_mov)
    img_mov = itk.image_view_from_array(img_mov)

    generateTmpTextforRegistration(points, path_txt)
    reg = transformix_filter(
        img_mov,
        transform_parameters,
        fixed_point_set_file_name=path_txt
    )

    points_reg = np.loadtxt('outputpoints.txt', dtype='str')
    if points_reg.ndim == 2: # for xy coords
        points_reg = points_reg[:,27:29].astype('float64').astype("uint32")
    elif points_reg.ndim == 1: # for med coords
        points_reg = points_reg[27:29].astype('float64').astype("uint32")

    os.remove(path_txt)
    os.remove("outputpoints.txt")
    return points_reg

# apply transform parameters to dict_roi_coords
def applyDictROICoordsTransform(
    img_mov: np.ndarray[np.uint8, Tuple[int, int]], 
    transform_parameters: elastixParameterObject, 
    dict_roi_coords: Dict[int, Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32], Tuple[int]]],
    path_txt: str= "./points_tmp.txt",
) -> Dict[int, Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32], Tuple[int]]]:
    dict_roi_coords_reg = {}
    x_max, x_min, y_max, y_min = img_mov.shape[1], 0, img_mov.shape[0], 0

    i = 0
    for roi_id, dict_coords in dict_roi_coords.items():
        if i % 10 == 0:
            print(f"processing {i}/{len(dict_roi_coords)}")
        i += 1
        med = np.array([dict_coords["med"]])
        xpix_ypix = np.array([dict_coords["xpix"], dict_coords["ypix"]]).T
        med_reg = applyPointTransform(img_mov, transform_parameters, med, path_txt)
        xpix_ypix_reg = applyPointTransform(img_mov, transform_parameters, xpix_ypix, path_txt)
        # clip the coords
        med_reg = np.clip(med_reg, 0, [x_max, y_max])
        xpix_ypix_reg = np.clip(xpix_ypix_reg, [x_min, y_min], [x_max, y_max])

        dict_roi_coords_reg[roi_id] = {"xpix": xpix_ypix_reg[:,0], "ypix": xpix_ypix_reg[:, 1], "med": med_reg}
    return dict_roi_coords_reg