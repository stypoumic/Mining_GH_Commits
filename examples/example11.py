from s7_CommitMatcher import CommitMatcher

if __name__ == "__main__":
	cmatcher = CommitMatcher()
	
	code_before ="""public static void copyFile(File sourceFile, File destFile) {
                     
                        FileChannel sourceChannel = null;
                        FileChannel destChannel = null;
                     
                        try {
                     
                            sourceChannel = new FileInputStream(sourceFile).getChannel();
                            destChannel = new FileOutputStream(destFile).getChannel();
                            sourceChannel.transferTo(0, sourceChannel.size(), destChannel);
                     
                        } catch (IOException ex) {
                            ex.printStackTrace();
                        }
                    }"""
	code_after = """public static void copyFile(File sourceFile, File destFile) {
 
                        try (
                     
                            FileChannel sourceChannel = new FileInputStream(sourceFile).getChannel();
                     
                            FileChannel destChannel = new FileOutputStream(destFile).getChannel();
                        ) {
                     
                            sourceChannel.transferTo(0, sourceChannel.size(), destChannel);
                     
                        } catch (IOException ex) {
                            ex.printStackTrace();
                        }
                    }"""

	results = cmatcher.search(code_before = code_before, code_after = code_after, score_by = {'code_additions': True, 'code_deletions': True})

	for result in results[:10]:
		print("Score %.3f Message: %s" %(result[-1], result[0]))


        # Expected output:
"""
Score 0.269 Message: Fix creating output log
Score 0.263 Message: Close `InputStream`s used inside `getBytes`
Score 0.262 Message: Close InputStream after reading it
Score 0.262 Message: ScriptRunner runs all args (Thanks the patch from cies.breijs@gmail.com
Score 0.262 Message: it of simplification
Score 0.260 Message: Closed FileInputStream which is not closed after reading from file
Score 0.258 Message: modify exception process when put buffer data
Score 0.254 Message: Stop NPE during setupPreview()
Score 0.251 Message: in search for a reason. also content was exposed to timing issues
Score 0.250 Message: Attempt to reconnect when we get disconnected. Sit in a loop until we
successfully connect.

Signed-off-by: Richard Jones <rj@metabrew.com>
"""        

