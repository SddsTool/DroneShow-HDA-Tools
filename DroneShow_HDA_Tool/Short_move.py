import hou
import numpy as np
from scipy.spatial import distance
from scipy.optimize import linear_sum_assignment

# ==========================================
# 1. 準備（ノードとジオメトリの取得）
# ==========================================
node = hou.pwd()
geo_out = node.geometry() # Input 0 (書き込み対象：現在地)

inputs = node.inputs()
geo_start = inputs[0].geometry()
geo_tgt   = inputs[1].geometry()

# ==========================================
# 2. データ準備（全員をエントリーさせてSciPyへ渡す）
# ==========================================
src_positions = np.array([pt.position() for pt in geo_start.points()])
tgt_positions = np.array([pt.position() for pt in geo_tgt.points()])

tgt_pts_count = len(geo_tgt.points())

tgt_colors = []
if geo_tgt.findPointAttrib("Cd"):
    tgt_colors = [pt.attribValue("Cd") for pt in geo_tgt.points()]
else:
    tgt_colors = [(1.0, 1.0, 1.0)] * tgt_pts_count

has_uv = geo_tgt.findPointAttrib("uv") is not None
tgt_uvs = []
if has_uv:
    tgt_uvs = [pt.attribValue("uv") for pt in geo_tgt.points()]

# ==========================================
# 3. SciPyによる最強の最適化（ハンガリアン法）
# ==========================================
print("SciPy Optimization Start...")

cost_matrix = distance.cdist(src_positions, tgt_positions, 'sqeuclidean')

row_ind, col_ind = linear_sum_assignment(cost_matrix)

print("SciPy Optimization Done.")

# ==========================================
# 4. 結果書き込み（VEXへの指示書作成）
# ==========================================
if not geo_out.findPointAttrib("target_P"):
    geo_out.addAttrib(hou.attribType.Point, "target_P", (0.0, 0.0, 0.0))

if not geo_out.findPointAttrib("target_pt"):
    geo_out.addAttrib(hou.attribType.Point, "target_pt", -1) 

if not geo_out.findPointAttrib("target_Cd"):
    geo_out.addAttrib(hou.attribType.Point, "target_Cd", (1.0, 1.0, 1.0))

if has_uv and not geo_out.findPointAttrib("target_uv"):
    geo_out.addAttrib(hou.attribType.Point, "target_uv", (0.0, 0.0, 0.0))

for i in range(len(row_ind)):
    src_idx = int(row_ind[i])      
    target_idx = int(col_ind[i])   

    P2 = tuple(tgt_positions[target_idx]) 

    pt = geo_out.iterPoints()[src_idx]
    
    pt.setAttribValue("target_P", P2)
    pt.setAttribValue("target_pt", target_idx)

    pt.setAttribValue("target_Cd", tgt_colors[target_idx])
        
    if has_uv:
        pt.setAttribValue("target_uv", tgt_uvs[target_idx])