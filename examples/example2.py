from s7_CommitMatcher import CommitMatcher

if __name__ == "__main__":
	cmatcher = CommitMatcher()
	results = cmatcher.search(message = "concurrent modification exception", score_by={'message': True})

	first_result = results[0]

	print("\n\nMessage: " + str(first_result[0]))
	print("\n\nCode Before:\n" + str(first_result[1]))
	print("\n\nCode After:\n" + str(first_result[2]))
	print("\n\nCode Deletions:\n" + str(first_result[3]))
	print("\n\nCode Additions:\n" + str(first_result[4]))

# Expected output:
"""

Message: fixed concurrent modification exception


Code Before:
public void refreshPartitions(Set<GlobalPartitionId> partitions){
  _partitions=partitions;
  for (  GlobalPartitionId p : _partitionToOffset.keySet()) {
    if (!partitions.contains(p))     _partitionToOffset.remove(p);
  }
}


Code After:
public void refreshPartitions(Set<GlobalPartitionId> partitions){
  _partitions=partitions;
  Iterator<GlobalPartitionId> it=_partitionToOffset.keySet().iterator();
  while (it.hasNext()) {
    if (!partitions.contains(it.next()))     it.remove();
  }
}


Code Deletions:
           for(GlobalPartitionId p : _partitionToOffset.keySet()) {
              if(!partitions.contains(p)) _partitionToOffset.remove(p);


Code Additions:
           Iterator<GlobalPartitionId> it = _partitionToOffset.keySet().iterator();
           while(it.hasNext()) {
               if(!partitions.contains(it.next())) it.remove();
"""
