# 4130 Claim Dependency Graph

```text
4001 global affine residual baseline
        |
        v
4080 local affine feasibility
        |
        v
4081c all-19 local non-affine T1 survival
        |
        +--> 4082 scale/lag robustness in survivor class
        |
        +--> 4084/4085 spatial and timing characterization
        |
        +--> 4086/4087 signed and failure-boundary heterogeneity
        |
        v
4088 bounded local non-affine T1 synthesis
        |
        +--> 4090/4094 no stable C,dCdt,R first/second moment closure
        |
        +--> 4100/4105 no event-timestamp excess after state matching
        |
        +--> 4120/4121/4125 observation-specific recent-history boundary
        |
        v
413x phenomenon-and-boundary evidence synthesis
```
