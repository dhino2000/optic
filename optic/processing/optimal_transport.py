from __future__ import annotations
from ..type_definitions import *
import ot
import numpy as np

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# import FGW package
import external
import FGW

# get distance matrix
def calculateDistanceMatrix(
        array_src: np.ndarray, 
        array_tgt: np.ndarray=None, 
        metric: str="minkowski", 
        p: int=2
        ) -> np.ndarray[Tuple[float, float]]:
    if array_tgt is None:
        return ot.dist(array_src, metric=metric, p=p) # intra group
    else:
        return ot.dist(array_src, array_tgt, metric=metric, p=p) # inter group
        
# get uniform weight
def getUniformWeight(n: int) -> np.ndarray[Tuple[float]]:
    return ot.unif(n)

# get optimal transport plan
def getOptimalTransportPlan(
        cost_inter: np.ndarray[Tuple[float, float]], 
        cost_intra_src: np.ndarray[Tuple[float, float]], 
        cost_intra_tgt: np.ndarray[Tuple[float, float]],
        weight_src: np.ndarray[Tuple[float]], 
        weight_tgt: np.ndarray[Tuple[float]],
        method: Literal["W", "GW", "FGW"],
        loss_fun: str="square_loss",
        alpha: float=0.1
        ) -> np.ndarray[Tuple[float, float]]:
    if method == "W":
        return ot.emd(weight_src, weight_tgt, cost_inter)
    elif method == "GW":
        return ot.gromov.gromov_wasserstein(cost_intra_src, cost_intra_tgt, weight_src, weight_tgt, loss_fun)
    elif method == "FGW":
        return FGW.fgw_lp(cost_inter, cost_intra_src, cost_intra_tgt, weight_src, weight_tgt, loss_fun=loss_fun, alpha=alpha)
    
# get One-to-One matching from optimal transport plan
def getOneToOneMatching(G, C, threshold=1e-6, max_cost=float('inf')):
    n_src, n_tgt = G.shape
    
    # Step 1: 輸送元、輸送先でサンプル数が少ない方を選択
    if n_src <= n_tgt:
        src_indices = np.arange(n_src)
        tgt_indices = np.arange(n_tgt)
    else:
        src_indices = np.arange(n_tgt)
        tgt_indices = np.arange(n_src)
        G = G.T
        C = C.T
    
    matches = {}
    used_tgt = set()
    
    # Step 2: 選択した方の番号を順に見ていく
    for src in src_indices:
        valid_tgts = np.where(G[src] > threshold)[0]
        
        # コスト関数が一定以上のペアを排除
        valid_tgts = [tgt for tgt in valid_tgts if C[src, tgt] <= max_cost]
        
        # Step 3: 閾値以上の輸送を行うペアが1つしかない場合
        if len(valid_tgts) == 1:
            tgt = valid_tgts[0]
            if tgt not in used_tgt:
                matches[src] = tgt
                used_tgt.add(tgt)
            continue
        
        # Step 4: 複数ある場合
        if len(valid_tgts) > 1:
            # コスト関数の値でソート
            sorted_tgts = sorted(valid_tgts, key=lambda x: C[src, x])
            
            for tgt in sorted_tgts:
                if tgt not in used_tgt:
                    matches[src] = tgt
                    used_tgt.add(tgt)
                    break
    
    # 元の順序に戻す
    if n_src > n_tgt:
        matches = {v: k for k, v in matches.items()}
    
    return matches

# calculate ROI matching
def calculateROIMatching(
        array_src: np.ndarray,
        array_tgt: np.ndarray,
        method: str,
        loss_fun: str="square_loss",
        alpha: float=0.1,
        threshold: float=1e-6,
        max_cost: float=float('inf')
        ) -> Dict[int, int]:
    C = calculateDistanceMatrix(array_src, array_tgt)
    C1 = calculateDistanceMatrix(array_src)
    C2 = calculateDistanceMatrix(array_tgt)
    a = getUniformWeight(len(array_src))
    b = getUniformWeight(len(array_tgt))

    if method == "WD-shape" or method == "WD-distance":
        method = "W"
    elif method == "GWD":
        method = "GW"
    elif method == "FGWD":
        method = "FGW"
    G = getOptimalTransportPlan(C, C1, C2, a, b, method, loss_fun, alpha)
    matches = getOneToOneMatching(G, C, threshold, max_cost)
    return matches