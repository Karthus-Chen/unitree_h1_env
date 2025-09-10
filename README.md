# 创建虚拟环境
```bash
conda create -n robot_sim python==3.10.16
conda activate robot_sim
pip install mujoco==3.2.2 -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install mujoco-python-viewer==0.1.4 -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install opencv-python -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install ruckig -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install urdf_parser_py -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install h5py -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install matplotlib -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install tqdm -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install einops -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install torch==2.8.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install torchvision==0.23.0 -i https://pypi.tuna.tsinghua.edu.cn/simple

conda install conda-forge::python-orocos-kdl
#conda install conda-forge::pinocchio
```

# 使用方法
```bash
#均在项目文件夹下运行 ~/unitree_h1_env$ xxxxx
#录制数据集
python3 DataCollecter/h1_record.py

#ACT
#训练
python3 ACT/demos/train_act.py
#推理
python3 ACT/demos/h1_act_eval.py --epoch 4000
```
