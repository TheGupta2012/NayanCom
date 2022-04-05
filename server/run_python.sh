#! /bin/bash

# bind the bt device first 
sudo rfcomm bind rfcomm1 98:D3:21:F7:7D:45 

# # # vital script
python -m python_model.NayanCom_vital &

# cv script
python -m python_model.NayanCom_cv --shape-predictor python_model/models/landmark.dat 