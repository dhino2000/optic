from __future__ import annotations
from ..type_definitions import *
import numpy as np
import itk
from itk.itkImagePython import itkImageUC2

def convertDictToElastixFormat(dict_params: Dict[str, Any]) -> Dict[str, Tuple[str]]:
    return {k: tuple(v) if isinstance(v, list) else (str(v),) for k, v in dict_params.items()}

def runElastix(
    img_fix: np.ndarray[np.uint8, Tuple[int, int]], 
    img_mov: np.ndarray[np.uint8, Tuple[int, int]], 
    parameter_map: Dict[str, Tuple[str]], 
    output_dir: str = None
) -> Tuple[np.ndarray[np.uint8, Tuple[int, int]], Any]:
    parameter_object = itk.ParameterObject.New()
    parameter_object.AddParameterMap(parameter_map)

    img_res, result_transform_parameters = itk.elastix_registration_method(img_fix, img_mov, parameter_object=parameter_object, output_dir=output_dir)
    return img_res, result_transform_parameters

def registerImageElastix(
    img_fix: np.ndarray[np.uint8, Tuple[int, int]], 
    img_mov: np.ndarray[np.uint8, Tuple[int, int]], 
    dict_params: Dict[str, Any], 
    output_dir: str = None
) -> Tuple[np.ndarray[np.uint8, Tuple[int, int]], Any]:
    parameter_map = convertDictToElastixFormat(dict_params)
    return runElastix(img_fix, img_mov, parameter_map, output_dir)