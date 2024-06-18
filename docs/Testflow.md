# Dependencies for Benchmarktests

The resources need to be created in this order taken from [api_monitor.sh](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L4300-L4335)

1. **createRouters**
1. **createNets**
1. **createSubNets**
1. **createRIfaces**
1. **createSGroups** (with conditions `-a -z "$INTERRUPTED"` and `! -e stop-os-hm`)
1. **createLBs**
1. **createJHVols**
1. **createVIPs**
1. **createJHPorts**
1. **createVols**
1. **createKeypairs**
1. **createPorts**
    - Followed by `waitJHVols`
1. **createJHVMs**
    - Set `ROUNDVMS=$NOAZS`
1. **createFIPs**
    - Followed by `waitVols`
1. **createVMs**
    - Update `ROUNDVMS`
    - Followed by `waitJHVMs`
    - Check result `RC`:
        - If `RC != 0`:
            - If `RC > $NOAZS`, adjust `VMERRORS`
        - If `RC == 0`:
            1. **loadbalancer**
            1. **waitLBs**
            1. **LBERRORS** based on `LBAASS`
            1. **waitVMs**
            1. **setmetaVMs**
1. **create2ndSubNets**
1. **create2ndPorts**


```mermaid
graph TD
    A[createRouters] -->|true| B[createNets]
    B -->|true| C[createSubNets]
    C -->|true| D[createRIfaces]
    D -->|true| E[createSGroups]
    E -->|true| F[createLBs]
    F --> G[createJHVols]
    G -->|true| H[createVIPs]
    H -->|true| I[createJHPorts]
    I -->|true| J[createVols]
    J -->|true| K[createKeypairs]
    K -->|true| L[createPorts]
    L --> M[waitJHVols]
    L --> N[createJHVMs]
    N -->|true| O[set ROUNDVMS]
    O --> P[createFIPs]
    P -->|true| Q[waitVols]
    Q --> R[createVMs]
    R -->|true| S[update ROUNDVMS]
    S --> T[waitJHVMs]
    T --> U{test RC != 0}
    U -->|true| V{test RC > NOAZS}
    V -->|true| W[update VMERRORS NOAZS]
    V -->|false| X[update VMERRORS RC]
    U -->|false| Y[loadbalancer]
    Y --> Z[waitLBs]
    Z --> AA{test LBAASS}
    AA -->|true| AB[set LBERRORS]
    Y --> AC[waitVMs]
    AC --> AD[setmetaVMs]
    AD --> AE[create2ndSubNets]
    AE --> AF[create2ndPorts]
