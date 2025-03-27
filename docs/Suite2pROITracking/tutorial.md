# Suite2pROITracking Tutorial
<img src="images/suite2p_roi_tracking.png">

**Suite2pROITracking** is an application developed for efficiently ROI tracking between different imaging sessions of the same subject. 
These ROI correspondence relationships are saved as .mat files to facilitate downstream analysis. 
Since this application depends on analysis results of [**Suite2pROICuration**](https://github.com/dhino2000/optic/edit/main/docs/Suite2pROICuration/tutorial.md), it is recommended to first perform ROI check.

## Workflow

1. **Load Fall.mat**
2. **Load ROICheck.mat**
3. [**Image registration**](#image-registration)
4. [**Auto ROI tracking**](#automatic-roi-matching)
5. **Check ROI tracking manually**
6. **Save ROITracking.mat file**

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
About secondary view section and secondary table section, the function is same as that of **Suite2pROICuration**.  

### Pri View Section
<table>
<tr>
<td width="50%">

- **View**
  
  display ROIs of Fall.mat, and the choosed ROI is highlighted. If **Macth_Cell_ID** is filled, white line between pri **Cell_ID** ROI and sec **Macth_Cell_ID** ROI is drawn. The opacity of white line can be changed with the slider of **Image Registration** section.
  - **Left mouse click** : Choose the closest ROI after passing ROI skip conditions
  - **Right mouse click** (only **pri** view) : Choose the closest ROI of **sec** view after passing ROI skip conditions

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
  - **Blue** : Secondary ROIs. Only ROIs of the celltype set in **ROI Display Setting** will be displayed.   

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

- **Cell_ID_Match**
  
  The table has additionaly column, **Cell_ID_Match**, the secondary ROI ID matched to the primary ROI ID.   
  Although ROI check is possible in also this application, creating ROICheck files using Suite2pROICuration is recommended for its more comprehensive functionality.  

  > ⚠️ **WARNING:**  
  > Before load ROICheck, please match the table columns with the table columns of the ROIcheck file.  
  > ex) NG: app; ["Cell_ID", "Cell_ID_Match", "Neuron", "Not_Cell", "Check"], ROICheck; ["Cell_ID", "Cell_ID_Match", "Astrocyte", "Not_Cell", "Check"]  

  Cell_ID_Match is initially blank, but a number is filled, a white line is drawn on the **View**. 
  This indicates which **sec** ROI matches to the **pri** ROI.   
  This number must be a integer value between 0 and the maximum ROI number in sec. 
  Since you typically would like to know the matching relationships of only neurons, you don't need to fill in all the blanks.   

- **one-to-one ROI matching**
  
  Also, the matching should basically be **one-to-one**, and you should avoid having one pri ROI matches to multiple sec ROIs, or vice versa.

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

**Image registration** supports **manual** ROI matching. 
While the ROI arrangement pattern is basically similar between the sessions from the same subject, image drifting noise makes ROI matching process difficult. 
In this section, image registration using [**ITKElastix**](https://github.com/InsightSoftwareConsortium/ITKElastix) is available. 
It performs registration from **sec (moving)** to **pri (fixed)** based on the background image, and applies the obtained transformation to the ROIs as well, enabling more efficient ROI matching by overlaying pri ROIs and sec ROIs.

This application has three types of image transformation, **Rigid**, **Affine**, and **B-Spline**.  
- **Performance comparison of image transformations**
<table>
  <tr>
    <td></td>
    <td> <b>Rigid </td>
    <td> <b>Affine </td>
    <td> <b>B-Spline </td>
  </tr>
  <tr>
    <td> <b>Computation Speed </td>
    <td> 0.5 ~ 1 (sec/image) </td>
    <td> 1 ~ 2 (sec/image) </td>
    <td> 2 ~ 4 (sec/image) </td>
  </tr>
  <tr>
    <td> <b>Degrees of Freedom </td>
    <td> Moderate </td>
    <td> Good </td>
    <td> Excellent </td>
  </tr>
  <tr>
    <td> <b>Shape Preservation </td>
    <td> Excellent </td>
    <td> Good </td>
    <td> Moderate </td>
  </tr>
  <tr>
    <td> <b>Robustness </td>
    <td> Good </td>
    <td> Good </td>
    <td> Good </td>
  </tr>
  <tr>
    <td> <b>Local Deformation Handling </td>
    <td> Poor </td>
    <td> Poor </td>
    <td> Excellent </td>
  </tr>
  <tr>
    <td> <b>Motion Correction </td>
    <td> Poor </td>
    <td> Moderate </td>
    <td> Excellent </td>
  </tr>
  <tr>
    <td> <b>Registration Accuracy </td>
    <td> Moderate </td>
    <td> Good </td>
    <td> Excellent </td>
  </tr>
</table>

First, set the **Elastix method**, and then set the **reference channel** (if the Fall is extracted from single-channel imaging, leave it as is). 
The configuration for the Elastix transformation method can be customized with **Elastix Config**. 
Click **Run Elastix** and wait for a while until the image registration is complete. 
You can monitor the progress on Anaconda Prompt.

</td>
<td width="50%">
  
<img src="images/suite2p_roi_tracking_image_registration.png">

- **Elastix Image Registration Config Window**
<img src="images/suite2p_roi_tracking_elastix_config.png">

</td>
</tr>
</table>

### Automatic ROI Matching
<table>
<tr>
<td width="50%">

Automatic ROI matching is also available. 
The number of ROI pairs with ROI matching often exceeds 100, manual ROI matching is time-consuming and labor-intensive even with the assistance of image registration. 
This automatic ROI matching function can significantly reduce the time and effort. 
Furthermore, combining it with manual corrections enables highly efficient and accurate ROI tracking.   
This section provides the tutorial of automatic ROI matching with [optimal transport](https://github.com/PythonOT/POT). 
The typical ROI tracking workflow involves first performing ROI classification with [Suite2pROICuration](https://github.com/dhino2000/optic/edit/main/docs/Suite2pROICuration/tutorial.md), then applying automatic ROI matching for specific cell types, and finally making manual adjustments to ensure matching accuracy. 
Image registration support can be utilized when necessary to improve the matching results.

- **Parameters for Optimal Transport**
  - **Loss**
    
    This application has four optimal transport loss function options: **WD(Wasserstein Distance)-shape**, **WD-distance**, **GWD(Gromov-Wasserstein Distance)**, and [**FGWD(Fused Gromov-Wasserstein Distance)**](https://github.com/tvayer/FGW/tree/master). The WD-distance exponent controls the distance weighting during matching; higher values discourage long-distance matching by penalizing distant pairs more heavily.
    The FGWD alpha parameter balances ROI shape similarity and distance penalty of matching; lower values prioritize distance penalty.
  - **pruning ROI matching**
    
    While optimal transport initially makes multi-to-multi ROIs matching, the algorithm applies a two-step pruning process to derive one-to-one ROI matching suitable for ROI tracking.
    First, **minimum transport value pruning algorithm** eliminates ROI pairs where the transport value is less than the threshold, **"Min transport threshold"**.
    Then, from the remaining pairs, the ROI pair with the highest transport value is choosed.
    Subsequently, through **maximum transport cost pruning algorithm**, if the transport cost of the pair exceeds **"Max cost threshold"**, the pri ROI is considered to not have matched ROI of sec.

- **ROI Matching Test Window**
  
  The **ROI Matching Test** provides a visual preview of optmial transport patterns between pri and sec ROIs.  
  - **Red dots** : the centers of pri ROIs  
  - **Blue dots** : the centers of sec ROIs  
  - **Green lines** : ROI matching between pri and sec.
    
  The transport plan with optimal transport is represented as a (source samples) × (destination samples) matrix, therefore the initial optimal transport result is exported as multi-to-multi ROI matching.
  Users can enable the "Plot Transport Plan" option to visualize this complete transport matrix before pruning.

- **Save, Load ROI Tracking result**
  
  The ROI matching results are saved as **ROITracking.mat** files, each file contains tracking data between two imaging sessions.
  For tracking across three or more sessions, you need to create ROITracking files for each session pair.
  For downstream analysis using these tracking results, please refer to the provided [Jupyter notebooks](https://github.com/dhino2000/optic).

</td>
<td width="50%">
  
<img src="images/suite2p_roi_tracking_roi_matching.png">

- **ROI Matching Test Window**
<img src="images/suite2p_roi_tracking_roi_matching_test.png">

</td>
</tr>
</table>

