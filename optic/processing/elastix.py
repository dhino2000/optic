from __future__ import annotations
from ..type_definitions import *
import os
import glob
import numpy as np
import time
import itk
from itk.elxParameterObjectPython import elastixParameterObject, mapstringvectorstring
from itk.itkElastixRegistrationMethodPython import elastix_registration_method
from itk.itkTransformixFilterPython import transformix_filter
from itk.ElastixPython import transformix_pointset

"""
preprocessing for elastix registration
"""
# convert params dictionary to elastix format
def convertDictToElastixFormat(
    dict_params: Dict[str, Any]
) -> Dict[str, Tuple[str]]:
    return {k: tuple(v) if isinstance(v, list) else (str(v),) for k, v in dict_params.items()}

# make elastix parameter object
def makeElastixParameterObject(
    parameter_map: mapstringvectorstring
) -> elastixParameterObject:
    parameter_object = elastixParameterObject.New()
    parameter_object.AddParameterMap(parameter_map)
    return parameter_object

# generate point's coordination file for elastix registration
def generateTmpTextforRegistration(
    coords: np.ndarray[np.uint8, Tuple[int, int]], 
    path_dst: str
) -> None:
    np.savetxt(path_dst, coords, fmt = "%d")
    # Modify the file
    with open(path_dst, 'r') as f:
        l = f.readlines()

    l.insert(0, 'point\n')
    l.insert(1, f'{len(coords)}\n')

    with open(path_dst, 'w') as f:
        f.writelines(l)

# make inversed elastix parameter object
def makeElastixParameterObjectInversed(
    parameter_map: mapstringvectorstring,
) -> elastixParameterObject:
    parameter_object_inverse = elastixParameterObject.New() # your parameter object for backward registration. 
    parameter_map_inverse = parameter_map.copy()

    parameter_map_inverse["Metric"] = ["DisplacementMagnitudePenalty"]
    parameter_map_inverse["HowToCombineTransforms"] = ["Compose"]
    # parameter_map_inverse["InitialTransformParametersFileName"] = ["NoInitialTransform"]
    parameter_map_inverse["UseDirectionCosines"] = ["true"]
    parameter_map_inverse["FixedInternalImagePixelType"] = ["float"]
    parameter_map_inverse["MovingInternalImagePixelType"] = ["float"]

    parameter_object_inverse.AddParameterMap(parameter_map_inverse)
    return parameter_object_inverse
    
    
"""
elastix registration
"""

# calculate transform parameters
def calculateSingleTransform(
    img_fix: np.ndarray[np.uint8, Tuple[int, int]], 
    img_mov: np.ndarray[np.uint8, Tuple[int, int]], 
    parameter_object: elastixParameterObject, 
    output_directory: str,
) -> elastixParameterObject:
    
    img_fix = np.ascontiguousarray(img_fix)
    img_mov = np.ascontiguousarray(img_mov)
    img_fix = itk.image_view_from_array(img_fix)
    img_mov = itk.image_view_from_array(img_mov)

    img_reg, transform_parameters = elastix_registration_method(
        img_fix, 
        img_mov, 
        parameter_object, 
        output_directory=output_directory
        )
    return transform_parameters

# apply transform parameters to single image
def applySingleTransform(
    img_mov: np.ndarray[np.uint8, Tuple[int, int]], 
    transform_parameters: elastixParameterObject, 
    output_directory: str,
) -> np.ndarray[np.uint8, Tuple[int, int]]:
    
    img_mov = np.ascontiguousarray(img_mov)
    img_mov = itk.image_view_from_array(img_mov)

    img_reg = transformix_filter(
        img_mov, 
        transform_parameters, 
        output_directory=output_directory
        )
    img_reg = itk.array_from_image(img_reg)
    return img_reg

# run elastix registration for single image
def runSingleRegistration(
    img_fix: np.ndarray[np.uint8, Tuple[int, int]], 
    img_mov: np.ndarray[np.uint8, Tuple[int, int]], 
    parameter_object: elastixParameterObject, 
    output_directory: str,
) -> np.ndarray[np.uint8, Tuple[int, int]]:
    transform_parameters = calculateSingleTransform(img_fix, img_mov, parameter_object, output_directory)
    img_reg = applySingleTransform(img_mov, transform_parameters, output_directory)
    return img_reg

# calculate transform parameters from image stack
def calculateStackTransform(
    img_stack: np.ndarray[np.uint8, Tuple[int, int, int, int, int]], # XYCZT
    parameter_object: elastixParameterObject, 
    channel_ref: int,
    idx_ref: int,
    axis: Literal["t", "z"],
    output_directory: str,
) -> Dict[str, elastixParameterObject]:
    dict_transform_parameters = {}

    if axis == "t": # register t-axis
        for z in range(img_stack.shape[3]):
            img_fix = img_stack[:, :, channel_ref, z, idx_ref]
            for t in range(img_stack.shape[4]):
                img_mov = img_stack[:, :, channel_ref, z, t]
                transform_parameters = calculateSingleTransform(img_fix, img_mov, parameter_object, output_directory)
                dict_transform_parameters[f"z{z}_t{t}"] = transform_parameters
                print("calculating", "z:", z, "t:", t)
    elif axis == "z": # register z-axis
        for t in range(img_stack.shape[4]):
            img_fix = img_stack[:, :, channel_ref, idx_ref, t]
            for z in range(img_stack.shape[3]):
                img_mov = img_stack[:, :, channel_ref, z, t]
                transform_parameters = calculateSingleTransform(img_fix, img_mov, parameter_object, output_directory)
                dict_transform_parameters[f"z{z}_t{t}"] = transform_parameters
                print("calculating", "z:", z, "t:", t)
    print("transform parameters calculation completed")
    return dict_transform_parameters

# apply transform parameters to image stack
def applyStackTransform(
    img_stack: np.ndarray[np.uint8, Tuple[int, int, int, int, int]], # XYCZT
    dict_transform_parameters: Dict[str, elastixParameterObject],
    output_directory: str,
) -> np.ndarray[np.uint8, Tuple[int, int]]:
    img_stack_reg = np.zeros_like(img_stack)
    num_c, num_z, num_t = img_stack.shape[2], img_stack.shape[3], img_stack.shape[4]
    for c in range(num_c):
        for z in range(num_z):
            for t in range(num_t):
                transform_parameters = dict_transform_parameters[f"z{z}_t{t}"]
                img_mov = img_stack[:, :, c, z, t]
                img_reg = applySingleTransform(img_mov, transform_parameters, output_directory)
                img_stack_reg[:, :, c, z, t] = img_reg
                print("applying", "c", c, "z:", z, "t:", t)
    print("image transformation completed")
    return img_stack_reg

# run elastix registration for image stack
def runStackRegistration(
    img_stack: np.ndarray[np.uint8, Tuple[int, int, int, int, int]], # XYCZT
    parameter_object: elastixParameterObject,
    channel_ref: int,
    idx_ref: int,
    axis: Literal["t", "z"],
    output_directory: str,
) -> np.ndarray[np.uint8, Tuple[int, int]]:
    dict_transform_parameters = calculateStackTransform(img_stack, parameter_object, channel_ref, idx_ref, axis, output_directory)
    img_stack_reg = applyStackTransform(img_stack, dict_transform_parameters, output_directory)
    return img_stack_reg

# apply transform parameters to points
"""
WARNING!!!
point transform is only fixed -> moving
so, transform parameters should be inversed
"""
def calculateSingleTransformInverse(
    img_fix: np.ndarray[np.uint8, Tuple[int, int]],
    img_mov: np.ndarray[np.uint8, Tuple[int, int]], 
    parameter_object_inverse: elastixParameterObject,
    path_transform_parameters_file: str,
    output_directory: str
) -> elastixParameterObject:
    img_fix = np.ascontiguousarray(img_fix)
    img_mov = np.ascontiguousarray(img_mov)
    img_fix = itk.image_view_from_array(img_fix)
    img_mov = itk.image_view_from_array(img_mov)

    img_reg_inverse, transform_parameters_inverse = elastix_registration_method(
        img_fix, img_fix,
        parameter_object=parameter_object_inverse, 
        output_directory=output_directory,
        initial_transform_parameter_file_name=path_transform_parameters_file,
        log_to_console=True,
        log_to_file=True
    )
    transform_parameters_inverse.SetParameter(0,"InitialTransformParameterFileName", "NoInitialTransform")

    return transform_parameters_inverse

def applyPointTransform(
    img_fix: np.ndarray[np.uint8, Tuple[int, int]],
    img_mov: np.ndarray[np.uint8, Tuple[int, int]], 
    transform_parameters_inverse: elastixParameterObject,
    path_points_txt: str,
    output_directory: str
) -> np.ndarray[np.int32, Tuple[int, int]]:
    img_fix = np.ascontiguousarray(img_fix)
    img_mov = np.ascontiguousarray(img_mov)
    img_fix = itk.image_view_from_array(img_fix)
    img_mov = itk.image_view_from_array(img_mov)

    result_point_set = transformix_pointset(
        img_mov, transform_parameters_inverse,
        fixed_point_set_file_name=path_points_txt,
        output_directory = output_directory,
        log_to_console=True,
        log_to_file=True)
    
    path_txt_output  = os.path.join(output_directory, "outputpoints.txt")

    points_reg = np.loadtxt(path_txt_output, dtype='str') # hardcoded, need to change
    if points_reg.ndim == 2: # for xy coords
        points_reg = points_reg[:,27:29].astype('float64').astype("uint32")
    elif points_reg.ndim == 1: # for med coords
        points_reg = points_reg[27:29].astype('float64').astype("uint32")
    
    return points_reg

# apply transform parameters to dict_roi_coords
def applyDictROICoordsTransform(
    img_fix: np.ndarray[np.uint8, Tuple[int, int]],
    img_mov: np.ndarray[np.uint8, Tuple[int, int]], 
    dict_roi_coords: Dict[int, Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32], Tuple[int]]],
    parameter_map: mapstringvectorstring,
    path_transform_parameters_file: str,
    path_points_txt: str,
    output_directory: str
) -> Dict[int, Dict[Literal["xpix", "ypix", "med"], np.ndarray[np.int32], Tuple[int]]]:
    dict_roi_coords_reg = {}
    x_max, x_min, y_max, y_min = img_mov.shape[1]-1, 0, img_mov.shape[0]-1, 0
    parameter_object_inverse = makeElastixParameterObjectInversed(parameter_map)
    transform_parameters_inverse = calculateSingleTransformInverse(
        img_fix, img_mov, 
        parameter_object_inverse, 
        path_transform_parameters_file, 
        output_directory
    )

    i = 0
    for roi_id, dict_coords in dict_roi_coords.items():
        if i % 100 == 0:
            print(f"processing {i}/{len(dict_roi_coords)}")
        i += 1
        med = np.array([dict_coords["med"]])
        xpix_ypix = np.array([dict_coords["xpix"], dict_coords["ypix"]]).T

        generateTmpTextforRegistration(xpix_ypix, path_points_txt)
        xpix_ypix_reg = applyPointTransform(
            img_fix, img_mov, 
            transform_parameters_inverse,
            path_points_txt, 
            output_directory
            )

        generateTmpTextforRegistration(med, path_points_txt)
        med_reg = applyPointTransform(
            img_fix, img_mov, 
            transform_parameters_inverse,
            path_points_txt, 
            output_directory
            )

        # clip the coords
        med_reg = np.clip(med_reg, 0, [x_max, y_max])
        xpix_ypix_reg = np.clip(xpix_ypix_reg, [x_min, y_min], [x_max, y_max])

        dict_roi_coords_reg[roi_id] = {"xpix": xpix_ypix_reg[:,0], "ypix": xpix_ypix_reg[:, 1], "med": med_reg}
    return dict_roi_coords_reg