# Bryan's notes for git/swf_python-avm2_AdobeSwfActionScript

# To run 'the usual' tests ...
cd tests/
pytest

# To run, say, just some tests ...
cd tests/
pytest -k "test_E_T1400 or test_T1400" -s

pytest -k "test_TEV2110" -s # inside test_Evony_vm.py, run test_TEV2110_InitAllClassClasses

# for the

# @tEv.p:tTEV2110IACC:197  #1 classes[1]=mx.core:IChildList init_ix=8
# = test_Evony_vm.py ; def test_TEV2110_InitAllClassClasses ; line 197
# = print(f'\n@{BM.LINE()} {BM.TERM_YLW()} #{n} classes[{ix}]={itemC.nam_name} init_ix={itemC.init_ix}{BM.TERM_RESET()}')

2025-09-02
# PS why did I make uncommitted duplicate avm2/abc/abc_types.py :28 to :29 of
ABCNamespaceIndex = NewType('ABCNamespaceIndex', int)
???

2025-09-02
# PS why make uncommitted changes to tests/test_Evony_vm.py
@@ -222,15 +222,28 @@
@@ -285,7 +298,7 @@
@@ -312,9 +325,12 @@
m2bk = machine_EvonyClient_N.method_to_body.keys()
...
& other stuff
???
