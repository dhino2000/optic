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

### View Section
<table>
<tr>
<td width="50%">

</td>
<td width="50%">

<img src="images/suite2p_roi_tracking_view_pri.png">

</td>
</tr>
</table>

### Table Section
<table>
<tr>
<td width="50%">

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

