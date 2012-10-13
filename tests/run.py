import sys
import os

from spec import eq_, skip, Spec, raises, ok_, trap

from invoke.run import run
from invoke.exceptions import Failure

from _utils import support


class Run(Spec):
    "run()"

    def setup(self):
        os.chdir(support)
        self.both = "echo foo && ./err bar"
        self.out = "echo foo"
        self.err = "./err bar"

    def return_code_in_result(self):
        """
        Result has .return_code (and .exited) containing exit code int
        """
        r = run(self.out, hide='both')
        eq_(r.return_code, 0)
        eq_(r.exited, 0)

    def nonzero_return_code_for_failures(self):
        result = run("false", warn=True)
        eq_(result.exited, 1)
        result = run("goobypls", warn=True, hide='both')
        eq_(result.exited, 127)

    def stdout_attribute_contains_stdout(self):
        eq_(run(self.out, hide='both').stdout, 'foo\n')

    def stderr_attribute_contains_stderr(self):
        eq_(run(self.err, hide='both').stderr, 'bar\n')

    def stdout_contains_both_streams_under_pty(self):
        r = run(self.both, hide='both', pty=True)
        eq_(r.stdout, 'foo\r\nbar\r\n')

    def stderr_is_empty_under_pty(self):
        r = run(self.both, hide='both', pty=True)
        eq_(r.stderr, '')

    @raises(Failure)
    def fast_failures(self):
        run("false")

    def run_acts_as_success_boolean(self):
        ok_(not run("false", warn=True))
        ok_(run("true"))

    def non_one_return_codes_still_act_as_False(self):
        ok_(not run("goobypls", warn=True, hide='both'))

    def warn_kwarg_allows_continuing_past_failures(self):
        eq_(run("false", warn=True).exited, 1)

    @trap
    def hide_both_hides_everything(self):
        run(self.both, hide='both')
        eq_(sys.stdall.getvalue(), "")

    @trap
    def hide_both_hides_everything_under_pty(self):
        run(self.both, hide='both', pty=True)
        eq_(sys.stdall.getvalue(), "")

    @trap
    def hide_out_only_hides_stdout(self):
        run(self.both, hide='out')
        eq_(sys.stdout.getvalue().strip(), "")
        eq_(sys.stderr.getvalue().strip(), "bar")

    @trap
    def hide_out_hides_both_when_pty_on(self):
        run(self.both, hide='out', pty=True)
        eq_(sys.stdout.getvalue().strip(), "")
        eq_(sys.stderr.getvalue().strip(), "")

    @trap
    def hide_err_only_hides_stderr(self):
        run(self.both, hide='err')
        eq_(sys.stdout.getvalue().strip(), "foo")
        eq_(sys.stderr.getvalue().strip(), "")

    @trap
    def hide_err_has_no_effect_when_pty_on(self):
        run(self.both, hide='err', pty=True)
        eq_(sys.stdout.getvalue().strip(), "foo\r\nbar")

    @trap
    def hide_None_hides_nothing(self):
        run(self.both, hide=None)
        eq_(sys.stdout.getvalue().strip(), "foo")
        eq_(sys.stderr.getvalue().strip(), "bar")

    @raises(ValueError)
    def hide_unknown_vals_raises_ValueError(self):
        run("command", hide="what")

    def hide_does_not_affect_capturing(self):
        eq_(run(self.out, hide='both').stdout, 'foo\n')

    def return_value_indicates_whether_pty_was_used(self):
        eq_(run("true").pty, False)
        eq_(run("true", pty=True).pty, True)

    def pty_defaults_to_off(self):
        eq_(run("true").pty, False)

    def ok_attr_indicates_success(self):
        eq_(run("true").ok, True)
        eq_(run("false", warn=True).ok, False)

    def failed_attr_indicates_failure(self):
        eq_(run("true").failed, False)
        eq_(run("false", warn=True).failed, True)
