# Suite2pROITracking Tutorial
<img src="images/suite2p_roi_tracking.png">

**Suite2pROITracking** is an application developed for efficiently ROI tracking between different imaging sessions of the same subject. 
These ROI correspondence relationships are saved as .mat files to facilitate downstream analysis. 
Since this application depends on analysis results of [**Suite2pROICheck**](https://github.com/dhino2000/optic/edit/main/docs/Suite2pROICheck/tutorial.md), it is recommended to first perform ROI check.

## Input
Before using this application, please prepare **Fall.mat**, and **ROICheck.mat**, the result of ROI check.  
- (Required): two **Fall.mat** and two **ROICheck.mat**

## Output
The result of ROI tracking is exported as **ROITracking~.mat**
- **ROITracking_{name_of_the_primary_Fall_file}.mat**

## Load Fall.mat file
<img src="images/suite2p_roi_tracking_file_load.png">


**Fall mat file path (Required):**   
push "browse" button and choose "Fall.mat" file. Suite2pROITracking needs two Fall.mat, **primary (pri)** and **secondary (sec)**. The "pri" serves as the reference side in ROI tracking. 
It is used to determine which ROIs in "pri" correspond to which ROIs in "sec". 

## Application interface

<img src="images/suite2p_roi_tracking_legend.png">

**Suite2pROITracking** consists of two major sections, **primary (pri)** and **secondary (sec)**, and each section consists of two minor sections, **View** and **Table**. 
About secondary view section and secondary table section, the function is same as that of **Suite2pROICheck**.  

### Pri View Section
<table>
<tr>
<td width="50%">

- **View**  
  display ROIs of Fall.mat, and the choosed ROI is highlighted.
  - **mouse click** : Choose the closest ROI after passing ROI skip conditions

- **ROI property**  
  These explanations are derived from the [Suite2p documentation](https://suite2p.readthedocs.io/en/latest/outputs.html).
  - **med** : (y,x) center of cell
  - **npix** : number of pixels in ROI
  - **npix_soma** : number of pixels in ROI's soma
  - **radius** : estimated radius of cell from 2D Gaussian fit to mask
  - **aspect_ratio** : ratio between major and minor axes of a 2D Gaussian fit to mask
  - **compact** : how compact the ROI is (1 is a disk, >1 means less compact)
  - **solidity** : unknown, maybe an parameter similar to compact?
  - **footprint** : spatial extent of an ROI’s functional signal, including pixels not assigned to the ROI; a threshold of 1/5 of the max is used as a threshold, and the average distance of these pixels from the center is defined as the footprint
  - **skew** : skewness of neuropil-corrected fluorescence trace
  - **std** : standard deviation of neuropil-corrected fluorescence trace
 
- **ROI Display Setting**  
  display all ROIs, none at all or only specific celltype ROIs.
  
- **Background Image Display Setting**  
  Suite2p generate four type background images, **meanImg**, **meanImgE**, **max_proj**, and **Vcorr**. you can switch between those images.

- **Skip ROIs with choosing**  
  When choosing ROIs, for example, if all **Neuron** ROIs have already been sorted and you want to concentrate on sorting only **Astrocyte** and **Not_Cell**, you can skip ROIs that are sorted to be **Neuron**. Similarly, it is possible to set skipping for other cell types.

- **Image Contrast**  
  - **Green** : Background image (**meanImg**, **meanImgE**, **max_proj**, and **Vcorr**) contrast of primary imaging channel.
  - **Red** : Background image (**meanImg**) contrast of seconday imaging channel. If the Fall.mat dosen't have secondary channel imaging data, this is meaningless. 
  - **Blue** : Background image contrast of reference tif image. If reference tif image is not set, this is meaningless. 

- **ROI Opacity**  
  Opacity of all and the selected ROI can be changed with the sliders.

</td>
<td width="50%">

<img src="images/suite2p_roi_tracking_view_pri.png">

</td>
</tr>
</table>

### Pri Table Section
<table>
<tr>
<td width="50%">

The table has additionaly column, **Cell_ID_Match**, the secondary ROI ID matched to the primary ROI ID.

> ⚠️ **WARNING:**  
> Before load ROICheck, please match the table columns with the table columns of the ROIcheck file.  
> ex) NG: app; ["Cell_ID", "Cell_ID_Match", "Neuron", "Not_Cell", "Check"], ROICheck; ["Cell_ID", "Cell_ID_Match", "Astrocyte", "Not_Cell", "Check"]  

</td>
<td width="50%">
  
<img src="images/suite2p_roi_tracking_table_pri.png">

</td>
</tr>
</table>

### Image Registration
<table>
<tr>
<td width="50%">

</td>
<td width="50%">
  
<img src="images/suite2p_roi_tracking_image_registration.png">

- **Elastix Image Registration Config Window**
<img src="images/suite2p_roi_tracking_elastix_config.png">

</td>
</tr>
</table>

### ROI Matching
<table>
<tr>
<td width="50%">

</td>
<td width="50%">
  
<img src="images/suite2p_roi_tracking_roi_matching.png">

- **ROI Matching Test Window**
<img src="images/suite2p_roi_tracking_roi_matching_test.png">

</td>
</tr>
</table>

