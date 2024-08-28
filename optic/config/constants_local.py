# アプリ間で共有する定数

# ローカル変数
# ROICheck.matのkeyに特別に追加する

class ROICheckMatKeysLocal:
    cell_type_keys = {
        "Neuron": "rows_selected_neuron",
        "Astrocyte": "rows_selected_astro",
        "Not Cell": "rows_selected_noise"
    }