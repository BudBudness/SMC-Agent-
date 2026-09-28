from smc_agent.smc_refinement import protected_swings,cluster_levels

def test_refinement():
    bars=[{"high":1,"low":0},{"high":3,"low":1},{"high":2,"low":0.5}]
    assert protected_swings(bars,1)
    assert len(cluster_levels([1,1.0001,2],.001))==2
