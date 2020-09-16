from s7_CommitMatcher import CommitMatcher

if __name__ == "__main__":
	cmatcher = CommitMatcher()
	
	code_before ="""public class Sum {
                        public static void main(String[] args) {
                            int a = 0;
                            int b = 0;
                     
                            try {
                                a = Integer.parseInt(args[0]);
                                b = Integer.parseInt(args[1]);
                     
                            } catch (NumberFormatException ex) {
                            }
                     
                            int sum = a + b;
                     
                            System.out.println("Sum = " + sum);
                        }
                    }"""
	code_after = """public class Sum {
                        public static void main(String[] args) {
                            int a = 0;
                            int b = 0;
                     
                            try {
                                a = Integer.parseInt(args[0]);
                                b = Integer.parseInt(args[1]);
                     
                            } catch (NumberFormatException ex) {
                                ex.printStackTrace();
                            }
                     
                            int sum = a + b;
                     
                            System.out.println("Sum = " + sum);
                        }
                    }"""

	results = cmatcher.search(code_before = code_before, code_after = code_after, score_by = {'code_additions': True, 'code_deletions': True})

	for result in results[:10]:
		print("Score %.3f Message: %s" %(result[-1], result[0]))
        
        # Expected output:
"""
Score 0.409 Message: Forces stack trace to be printed when a frame task fails.

Signed-off-by: Jared Woolston <Jared.Woolston@gmail.com>
Score 0.409 Message: Fixed un-logged exception.

Fixed error where exceptions would silently fail without reporting their
cause. We should always log exceptions when we catch them and do not
rethrow
Score 0.409 Message: Export: Add debug verbosity for the Nexus One
Score 0.409 Message: Add test output
Score 0.409 Message: Added stacktrace for errors
Score 0.300 Message: Calling close() hook when closing the actual 
socket
Score 0.298 Message: add logError back
Score 0.250 Message: Forgot to bind before testing in AbstractBindTest (DIRMINA-293)

git-svn-id: https://svn.apache.org/repos/asf/directory/trunks/mina@467906 13f79535-47bb-0310-9956-ffa450edef68
Score 0.250 Message: ARQ-168 ARQ-311 Added validate() method for configurations
Score 0.250 Message: fixed missing call to save() method
"""


