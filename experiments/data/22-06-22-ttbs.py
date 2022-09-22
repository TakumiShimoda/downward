#! /usr/bin/env python

import os
import shutil

import project


REPO = project.get_repo_base()
BENCHMARKS_DIR = os.environ["DOWNWARD_BENCHMARKS"]
# SCP_LOGIN = "myname@myserver.com"
SCP_LOGIN = "172.17.0.2"
REMOTE_REPOS_DIR = "/infai/seipp/projects"
if project.REMOTE:
    SUITE = project.SUITE_SATISFICING
    ENV = project.BaselSlurmEnvironment(email="my.name@myhost.ch")
else:
    SUITE = ["agricola-sat18-strips", "airport", "barman-sat11-strips",
    "barman-sat14-strips", "blocks","childsnack-sat14-strips",
    "data-network-sat18-strips", "depot", "driverlog",
    "elevators-sat08-strips", "elevators-sat11-strips",
    "floortile-sat11-strips", "floortile-sat14-strips", "freecell",
    "ged-sat14-strips", "grid", "gripper", "hiking-sat14-strips",
    "logistics00", "logistics98", "maintenance-sat14-adl", "miconic",
    "movie", "mprime", "mystery",
    "nomystery-sat11-strips",  "openstacks-sat08-strips",
    "openstacks-sat11-strips", "openstacks-sat14-strips", "openstacks-strips",
    "organic-synthesis-sat18-strips",
    "organic-synthesis-split-sat18-strips", "parcprinter-08-strips",
    "parcprinter-sat11-strips", "parking-sat11-strips", "parking-sat14-strips",
    "pathways", "pegsol-08-strips", "pegsol-sat11-strips",
    "pipesworld-notankage", "pipesworld-tankage", 
    "psr-small", "rovers", "satellite", "scanalyzer-08-strips",
    "scanalyzer-sat11-strips", "schedule", 
    "snake-sat18-strips", "sokoban-sat08-strips", "sokoban-sat11-strips",
    "spider-sat18-strips", "storage", "termes-sat18-strips",
    "tetris-sat14-strips", "thoughtful-sat14-strips", "tidybot-sat11-strips",
    "tpp", "transport-sat08-strips", "transport-sat11-strips",
    "transport-sat14-strips","trucks-strips",
    "visitall-sat11-strips", "visitall-sat14-strips",
    "woodworking-sat08-strips", "woodworking-sat11-strips", "zenotravel",]
    # SUITE = ["depot:p01.pddl", "grid:prob01.pddl", "gripper:prob01.pddl"]
    ENV = project.LocalEnvironment(processes=2)

CONFIGS = [
    (f"{index:02d}-{h_nick}", ["--search", f"astar(goalcount())"])
    for index, (h_nick, h) in enumerate(
        [
            # ("mybfs", "mybfs()"),
            # ("regression_test", "regression_test()"),
            # ("goalcount","goalcount()")
            ("TTBBS_K=3","TTBBS_K=3()")
            # ("TTBS","TTBS()")
        ],
        start=1,
    )
]
BUILD_OPTIONS = []
DRIVER_OPTIONS = ["--overall-time-limit", "10s","--overall-memory-limit","4G"]
REVS = [
    ("release-20.06.0", "20.06"),
]
ATTRIBUTES = [
    "error",
    # "run_dir",
    # "search_start_time",
    # "search_start_memory",
    "total_time",
    # "initial_h_value",
    # "h_values",
    "coverage",
    "expansions",
    "cost",
    project.MEET,
    # "memory",
    # project.EVALUATIONS_PER_TIME,
]

exp = project.FastDownwardExperiment(environment=ENV)
for config_nick, config in CONFIGS:
    for rev, rev_nick in REVS:
        algo_name = f"{rev_nick}:{config_nick}" if rev_nick else config_nick
        exp.add_algorithm(
            algo_name,
            REPO,
            rev,
            config,
            build_options=BUILD_OPTIONS,
            driver_options=DRIVER_OPTIONS,
        )
exp.add_suite(BENCHMARKS_DIR, SUITE)

exp.add_parser(exp.EXITCODE_PARSER)
exp.add_parser(exp.TRANSLATOR_PARSER)
exp.add_parser(exp.SINGLE_SEARCH_PARSER)
exp.add_parser(project.DIR / "parser.py")
exp.add_parser(exp.PLANNER_PARSER)

exp.add_step("build", exp.build)
exp.add_step("start", exp.start_runs)
exp.add_fetcher(name="fetch")

if not project.REMOTE:
    exp.add_step("remove-eval-dir", shutil.rmtree, exp.eval_dir, ignore_errors=True)
    project.add_scp_step(exp, SCP_LOGIN, REMOTE_REPOS_DIR)

project.add_absolute_report(
    exp, attributes=ATTRIBUTES
)

# attributes = ["total_time","expansions"]
attributes = []
pairs = [
    ("20.06:01-cg"),
]
suffix = "-rel" if project.RELATIVE else ""
for algo1 in pairs:
    for attr in attributes:
        exp.add_report(
            project.ScatterPlotReport(
                relative=project.RELATIVE,
                get_category=None if project.TEX else lambda run1, run2: run1["domain"],
                attributes=[attr],
                filter_algorithm=[algo1],
                filter=[project.add_meet],
                format="tex" if project.TEX else "png",
            ),
            name=f"{exp.name}-{algo1}-{attr}{suffix}",
        )

exp.run_steps()