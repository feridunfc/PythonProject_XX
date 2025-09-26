from pythonproject_xx.utils.sandbox import SandboxRunner
def test_syntax_ok():
    sb=SandboxRunner(); code,_,_=sb.syntax_check('x.py','print(\'ok\')'); assert code==0
def test_syntax_fail():
    sb=SandboxRunner(); code,_,_=sb.syntax_check('x.py','def :'); assert code!=0
