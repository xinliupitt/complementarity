# Complementarity

This repo provides information for the manuscript "Uncovering and estimating complementarity in urban lives".

If readers can fetch the Foursquare Future Cities Challenge dataset, they can input the data into the following files to fetch some key ideas introduced in the manuscript.

`simulation_chicago_period_b_nb.py` is to generate the simulated data to represent the base demand. Sample command to run this file:
```
thread_idx=20

this_period="overnight"

log_name="/ihome/kpelechrinis/xil178/simulation_chicago"
log_name+="_${this_period}_${thread_idx}.txt"

# Run the job
python simulation_chicago_period_b_nb.py\
    --thread $thread_idx\
    --start_B B\
    --end_B B\
    --period $this_period\
    &> $log_name
```

`mixed_effects.r` is for the mixed-effect model.

`gnn_model.ipynb` is for the graph neural network model.
