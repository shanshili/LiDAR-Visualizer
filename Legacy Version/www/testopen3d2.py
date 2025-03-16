
import open3d
import numpy as np

# 绘制open3d坐标系
axis_pcd = open3d.geometry.TriangleMesh.create_coordinate_frame(size=0.5, origin=[0, 0, 0])
# 在3D坐标上绘制点：坐标点[x,y,z]对应R，G，B颜色
points = np.array([[0.1, 0.1, 0.1], [1, 0, 0], [0, 1, 0], [0, 0, 1]])
colors = [[1, 1, 1], [1, 0, 0], [0, 1, 0], [0, 0, 1]]
 
test_pcd = open3d.geometry.PointCloud()  # 定义点云
 
# 方法1（非阻塞显示）
vis = open3d.visualization.Visualizer()
vis.create_window(window_name="Open3D1")
vis.get_render_option().point_size =0.5
# 先把点云对象添加给Visualizer
vis.add_geometry(axis_pcd)
vis.add_geometry(test_pcd)
while True:
    # 给点云添加显示的数据
    points -= 0.001
    test_pcd.points = open3d.utility.Vector3dVector(points)  # 定义点云坐标位置
    test_pcd.colors = open3d.utility.Vector3dVector(colors)  # 定义点云的颜色
    # update_renderer显示当前的数据
    vis.update_geometry()
    vis.poll_events()
    vis.update_renderer()
