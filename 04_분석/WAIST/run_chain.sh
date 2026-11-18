#!/bin/bash
# Full model chain for the WAIST analysis (principal model, multiverse, sensitivity suite, space-time interaction and spatial confounding models).
set -x
export SK_RSLOTS=7
S="${ST_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"; cd "$S"; RS="$S/01_스크립트/rslot.sh"
T=WAIST; GR="$S/04_분석/$T/graph_593.graph"; D=261118; NW=3; NMV=200
q(){ while [ "$(jobs -rp | wc -l)" -ge 3 ]; do sleep 10; done; }
lw(){ while [ "$(sysctl -n vm.loadavg | awk '{print int($3)}')" -ge 14 ]; do sleep 600; done; }
nice -n 10 env ST_VER=main python3 01_스크립트/80_build_disease_panel_v.py $T > 04_분석/$T/run_80v2.log 2>&1 || exit 1
lw
( for V in s577 s2 sc aux; do lw; ST_VER=$V python3 01_스크립트/80_build_disease_panel_v.py $T && (cd 01_스크립트 && ST_VER=$V ST_THREADS=1 ST_MV_N=2 ST_GRAPH=$([ $V = s577 ] || echo "$GR") $RS Rscript 81_fit_inla.R $T); done > 04_분석/$T/run_sens3v2.log 2>&1 ) &
export ST_VER=main ST_THREADS=1 ST_GRAPH="$GR"
lw; (cd 01_스크립트 && $RS Rscript 81_fit_inla.R $T) > 04_분석/$T/run_81a.log 2>&1 || exit 1
python3 01_스크립트/82L_core_report_nwin.py $T $D > 04_분석/$T/run_82.log 2>&1
python3 01_스크립트/83_check_report.py $T $D >> 04_분석/$T/run_82.log 2>&1
echo "CHAIN done"
python3 01_스크립트/87_window_grid.py $T main; (cd 01_스크립트 && TAG=$T ST_VER=main $RS Rscript 85_window_maps.R $T main); python3 01_스크립트/86_yearly_maps_ehsa_waist.py $T main
python3 01_스크립트/88g_sens_prep.py $T main METSC || exit 1
cd 01_스크립트; export TAG=$T NCO=METSC
L=../04_분석/$T
for G in 1 2 3 4 5 6; do q; lw; GROUP=$G $RS Rscript 88g_sens_suite_waist.R > $L/run_88g_$G.log 2>&1 & sleep 5; done
q; lw; $RS Rscript 88h_ppc_varpart.R > $L/run_88h.log 2>&1 &
for G in nb struct kh review; do q; lw; $RS Rscript 88k_struct_kh_waist.R $G > $L/run_88k_$G.log 2>&1 & sleep 5; done
wait
if grep -q 'KH_typeII FAILED' $L/run_88k_kh.log; then mv $L/results_main/S43_part_KH_typeII.csv $L/results_main/S43_part_KH_typeII_failed_init.csv.bak; KH_INIT=0 $RS Rscript 88k_struct_kh_waist.R kh > $L/run_88k_kh_init0.log 2>&1; fi
cd ..; TAG=$T ST_VER=main python3 01_스크립트/89g_sens_combine.py $T main > 04_분석/$T/run_89g.log 2>&1
echo "ALL rc=$?"; grep -l "FAILED" 04_분석/$T/run_88*.log; true
cd "$S"; lw; ST_VER=rep python3 01_스크립트/80_build_disease_panel_v.py $T > 04_분석/$T/run_80rep.log 2>&1 && (cd 01_스크립트 && ST_VER=rep ST_THREADS=1 ST_MV_N=2 ST_GRAPH="$GR" $RS Rscript 81_fit_inla.R $T) > 04_분석/$T/run_rep_81.log 2>&1
echo "REP rc=$?"

(cd 01_스크립트 && for G in conf period; do $RS Rscript 88k_struct_kh_waist.R $G; done)
