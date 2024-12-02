# Suite2pROICheck Tutroal
<img src="images/suite2p_roi_check.png">

## Load Fall.mat file
<img src="images/suite2p_roi_check_file_load.png">


**Fall mat file path (Necessary):**   
push "browse" button and choose "Fall.mat" file.  
Suite2pROICheck supports 2-channel imaging Fall.mat but not support multi-plane imaging data.  

**Reference tif image file path (Optional):**   
push "browse" button and choose single XY tif image file.  
If you capture reference image as tif file, you can use it with blue-channel image.

## Check ROIs
<img src="images/suite2p_roi_check_legend.png">

Suite2pROICheck consists of 3 GUI sections, **Canvas**, **View**, and **Table**.

### Canvas Section
<table>
<tr>
<td width="50%">

Your text content goes here. You can use regular markdown syntax inside the td tags.
- List item 1 
- List item 2

</td>
<td width="50%">

<img src="images/suite2p_roi_check_canvas.png">

</td>
</tr>
</table>

### View Section
<table>
<tr>
<td width="50%">

Your text content goes here. You can use regular markdown syntax inside the td tags.
- List item 1 
- List item 2

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

Your text content goes here. You can use regular markdown syntax inside the td tags.
- List item 1 
- List item 2

</td>
<td width="50%">

<img src="images/suite2p_roi_check_table.png">

</td>
</tr>
</table>

#### Key operation
☆ This operation is for table columns ["Cell_ID", "Astrocyte", "Neuron", "Not_Cell", "Check", "Tracking", "Memo"]. The Operation depends on the table columns settings.
<pre>
 - Z          : Choose Astrocyte        
 - X          : Choose Neuron           
 - C          : Choose Not_Cell         
 - V          : Check/Uncheck Check     
 - B          : Check/Uncheck Tracking  
 - up-arrow   : Move one row up         
 - down-arrow : Move one row down       
</pre>

## Custom Table Columns Configuration
The default columns configuration of Suite2pROICheck is ["Cell_ID", "Astrocyte", "Neuron", "Not_Cell", "Check", "Tracking", "Memo"], but you can custom them with **Table Columns Config** of Table section.

### Table Columns Config
<table>
<tr>
<td width="50%">

**Column Name**  
The name of table column, you can edit it freely.
> ⚠️ **WARNING:**  
> **Please do not contain "space" !!! Please use "_" instead !!!**  
> NG: "cell A" , OK: "cell_A"

**Type**  
id:  
celltype:  
checkbox:  
string:

**Width**

</td>
<td width="50%">

<img src="images/suite2p_roi_check_table_config.png">

</td>
</tr>
</table>

<table>
<tr>
<td width="50%">

Your text content goes here. You can use regular markdown syntax inside the td tags.
- List item 1 
- List item 2

</td>
<td width="50%">

<img src="images/suite2p_roi_check_table_config_custom.png">

</td>
</tr>
</table>



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
