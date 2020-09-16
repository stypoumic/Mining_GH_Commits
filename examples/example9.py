from s7_CommitMatcher import CommitMatcher

if __name__ == "__main__":
	cmatcher = CommitMatcher()
	
	code_before ="""public class Sample_String {
                        public static void main(String[] args) {
                            String S1 = "Example";
                            if (S1.isEmpty())   return 0;
                            return 1;
                        }
                    }"""
	code_after ="""public class Sample_String {
                        public static void main(String[] args) {
                            String S1 = "Example";
                            if (S1.length()>0)   return 0;
                            return 1;
                        }
                    }"""

	results = cmatcher.search(code_before = code_before, code_after = code_after, score_by = {'code_additions': True, 'code_deletions': True})

	for result in results[:10]:
		print("Score %.3f Message: %s" %(result[-1], result[0]))


# Expected output:
"""
Score 0.795 Message: Replaced a java 6 method with a java 5 equivalent

git-svn-id: https://svn.apache.org/repos/asf/hadoop/zookeeper/trunk@678868 13f79535-47bb-0310-9956-ffa450edef68
Score 0.795 Message: Make password validity check Java 5 compatible
Score 0.757 Message: Removed isEmpty for old VM compatibility
Score 0.757 Message: Removed isEmpty for old VM compatibility
Score 0.627 Message: Replace String.isEmpty() with String.length() == 0.

Older verisons of Android don't support String.isEmpty()
Score 0.618 Message: Removed call to Java 6 API
Score 0.575 Message: Fix broken Java 1.5 compatibility
Score 0.550 Message: Use String.length() instead of .isEmpty() to satisfy limitations on pre-level 9 Android clients
Score 0.513 Message: Use length==0 instead of "isEmpty" which crashes on Android 2.2 where the method is missing
Score 0.513 Message: Use length==0 instead of "isEmpty" which crashes on Android 2.2 where the method is missing
"""