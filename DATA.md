# Data Notes

The raw three-dimensional laboratory midge-swarm trajectories are external data
and are not bundled in this repository. They should be obtained from the
published data source cited in the manuscript.

For a full rerun, place the trajectory files in a local directory and pass that
directory with `--data-dir`. The historical local working path was a Windows
path, but it is not required for reproduction. Use an explicit argument such as:

```bash
python Experiment/run_4155_parallel_highB_omnibus_null.py --data-dir /path/to/raw_trajectories
```

The scripts expect observation files corresponding to the 19 laboratory
recordings, for example `Ob1.txt` through `Ob19.txt` or equivalent filenames
used by the published dataset.

Large generated frame-level tables and caches are intentionally not included in
this GitHub package. The central high-replicate null output and the final
manuscript freeze are included under `Output/4155/` and `Output/4156/`.
