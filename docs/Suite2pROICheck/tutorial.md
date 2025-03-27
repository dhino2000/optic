# Suite2pROICuration Tutorial
<img src="images/suite2p_roi_check.png">

**Suite2pROICuration** is a specialized tool for quickly and efficiently classifying ROIs extracted by Suite2p into neurons and noise cells. The interface is designed to be intuitive and visually clear. It can be customized to classify cells beyond neurons, allowing users to define their own cell types. By loading event files (.npy) from behavioral experiments simultaneously done with imaging, users can identify event-responsive cells.

## Workflow

1. **Load Fall.mat**
2. [**Set celltypes with table column config**](#custom-table-columns-configuration)
3. [**Check ROIs**](#check-rois)
4. **Save ROICheck.mat file**

## Input

Before using this application, please prepare **Fall.mat**, the result file of Suite2p.  
- (Required): **Fall.mat**
- (Optional): **single tif image**  

## Output

The result of ROI checking is exported as **ROICheck~.mat**, containing the ROI celltype information and can store multiple results. About downstream analysis, please check the [notebook for analysis](https://github.com/dhino2000/optic/blob/main/notebook/Chapter1_ExtractTracesWithCheckedROIs.ipynb).  
If you want to track ROIs between the different dates, please use [**Suite2pROITracking**](https://github.com/dhino2000/optic/blob/main/docs/Suite2pROITracking/tutorial.md).
- **ROICheck_{name_of_the_Fall_file}.mat**

## Load Fall.mat file
<img src="images/suite2p_roi_check_file_load.png">


**Fall mat file path (Required):**   

push "browse" button and choose "Fall.mat" file.  
Suite2pROICuration supports 2-channel imaging Fall.mat but not support multi-plane imaging data.  

**Reference tif image file path (Optional):**   

push "browse" button and choose single XY tif image file.  
If you capture reference image as tif file, you can use it with blue-channel image.

## Check ROIs
<img src="images/suite2p_roi_check_legend.png">

Suite2pROICuration consists of 3 GUI sections, **Canvas**, **View**, and **Table**.

### Canvas Section
<table>
<tr>
<td width="50%">

- **Top Axis**
  
  display zoomed traces (F, Fneu, spks) of the selected ROI.
  - **mouse drag** : move display area
  - **mouse scrool** : zoom in/out
  - **Minimum Plot Range** : set minimum display time in seconds

- **Middle Axis**
  
  display overall traces (F, Fneu, spks) of the selected ROI.  
  - **mouse click** : centers top axis view on clicked position
   
- **Bottom Axis**
  
  display average traces (F, Fneu, spks) across all ROIs.  
  When event file is loaded, display event-aligned F trace of the selected ROI.  

- **Event File**
  
  - **Event File** : The npy file containing experimental events. The content must consist of only 0 and 1 in a format like [0, 0, 1, 1, 1, 0, 0, ...].
  - **Plot Range** : Sets display range (seconds) before/after each event onset. With multiple events, all events are overlaid. **r** : Pearson correlation coefficient between trace and event. 

- **Light Mode**
  
  Reduces CPU load by downsampling plot points. When set to 250, plots 1,000 points (4x the value).

</td>
<td width="50%">

<img src="images/suite2p_roi_check_canvas.png">

- **With event file load**  
  1: Whisker stimulation ON, 0: Whisker simulation OFF

<img src="images/suite2p_roi_check_event_canvas.png">

</td>
</tr>
</table>

### View Section
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

<img src="images/suite2p_roi_check_view.png">

</td>
</tr>
</table>

### Table Section
<table>
<tr>
<td width="50%">

- **Table**
  
  The attributes of the columns are "id", "celltype", "check", and "string". The "celltype" determines the ROI's cell type by selecting one from the radio buttons. "check" and "string" are optional and can be left empty.

- **Table Columns Config**
  
  Table columns can be customized with [Table Columns Config](#custom-table-columns-configuration).

- **Set ROI celltype**
  
  The celltype, check values of the multiple ROIs from **index_min** to **index_max** can be changed simultaneously. Specifically for "celltype", changes can be configured for each checkbox.  
ex):
**index_min**: 100, **index_max**: 300, "Set **Neuron**", "Skip **Check** Checked", "Not Skip **Tracking** Checked"  
-> Only ROIs between indices 100-300 whose "Check" are unchecked will be changed to Neuron type.

- **Filter ROI**
  
  ROIs can be filtered based on six parameters: **npix**, **radius**, **aspect_ratio**, **compact**, **skew**, and **std**. If the all parameters of the ROI are not between the thresholds (min, max), the ROI's cell type will be switched to **Not_Cell**.

- **Save/Load ROI Check result**

  The results are saved as **ROICheck.mat** files.
  You can save your progress and resume ROI checking later by loading the file.
  When saving, you need to select a username, which can be edited in the **optic/config/json/user_settings.json**.  
  The ROICheck.mat file contains all previous checking results, allowing you to select any save point when loading.
  For downstream analysis using these ROICheck files, please refer to the provided [Jupyter notebooks](https://github.com/dhino2000/optic/blob/main/notebook/Chapter1_ExtractTracesWithCheckedROIs.ipynb).

</td>
<td width="50%">

<img src="images/suite2p_roi_check_table.png">

- **ROI celltype set**

<img src="images/suite2p_roi_check_roi_set.png">

- **Save Dialog**

<img src="images/user_select.png">

</td>
</tr>
</table>

#### Key operation of table

☆ This operation is for table columns ["Cell_ID", "Astrocyte", "Neuron", "Not_Cell", "Check", "Tracking", "Memo"]. The Operation depends on the table columns settings.
<pre>
 - Z          : Choose Astrocyte        
 - X          : Choose Neuron           
 - C          : Choose Not_Cell         
 - V          : Check/Uncheck Check     
 - B          : Check/Uncheck Tracking  
 - Y/H        : Move to previous/next ROI with the celltype selected in the "ROI Display Setting"  
 - U/J        : Move to previous/next ROI with the same celltype as the currently selected ROI  
 - I/K        : Move to previous/next ROI whose "Check" is checked  
 - O/L        : Move to previous/next ROI whose "Check" is unchecked  
 - up-arrow   : Move one row up         
 - down-arrow : Move one row down       
</pre>

## Custom Table Columns Configuration

The default columns configuration of Suite2pROICuration is ["Cell_ID", "Astrocyte", "Neuron", "Not_Cell", "Check", "Tracking", "Memo"], but you can custom them with **Table Columns Config** of Table section.

### Table Columns Config
<table>
<tr>
<td width="50%">

**Column Name**  

The name of table column, you can edit it freely, but with some restrictions.  
> ⚠️ **WARNING:**  
> **Please do not contain "space" !!! Please use "_" instead !!!**  
> NG: "cell A" , OK: "cell_A"  
> **please set the last "celltype" column as "Not_Cell" !!!**  
> NG: [Astrocyte, Not_Cell, Neuron] , OK: [Neuron, Astrocyte, Not_Cell]  

**Type**  

<pre>
id       : ROI number starting from 0. Uneditable.
celltype : Only one can be selected from multiple radio buttons.
checkbox : A checkbox value stored as a boolean (0/1).
string   : Memo, can contain text input. ⚠️: Please use only English or number.
</pre>

**Width**  

The Column width. it can be adjusted by dragging.  

</td>
<td width="50%">

- **Default**  
<img src="images/suite2p_roi_check_table_config.png">

- **After Customization**  
<img src="images/suite2p_roi_check_table_config_custom.png">

</td>
</tr>
</table>


<img src="images/suite2p_roi_check_custom.png">

#### Key operation of table

☆ This operation is for table columns ["Cell_ID", "Cell_A", "Cell_B", "Cell_C", "Not_Cell", "Check_A", "Check_B", "Check_C", "Memo"].
<pre>
 - Z          : Choose Cell_A        
 - X          : Choose Cell_B           
 - C          : Choose Cell_C         
 - V          : Choose Not_Cell     
 - B          : Check/Uncheck Check_A  
 - N          : Check/Uncheck Check_B  
 - M          : Check/Uncheck Check_C  
 - up-arrow   : Move one row up         
 - down-arrow : Move one row down       
</pre>
