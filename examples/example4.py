from s7_CommitMatcher import CommitMatcher

if __name__ == "__main__":
	cmatcher = CommitMatcher()
	results = cmatcher.search(message = "null pointer exception", score_by={'message': True})

	first_result = results[0]

	print("\n\nMessage: " + str(first_result[0]))
	print("\n\nCode Before:\n" + str(first_result[1]))
	print("\n\nCode After:\n" + str(first_result[2]))
	print("\n\nCode Deletions:\n" + str(first_result[3]))
	print("\n\nCode Additions:\n" + str(first_result[4]))

# Expected output:
"""

Message: Fixed null pointer exception


Code Before:
private Observable<BookmarkViewAdapter> initBookmarkManager(){
  return Observable.create(new Action<BookmarkViewAdapter>(){
    @Override public void onSubscribe(    @NonNull Subscriber<BookmarkViewAdapter> subscriber){
      mBookmarkAdapter=new BookmarkViewAdapter(getContext(),mBookmarks);
      setBookmarkDataSet(mBookmarkManager.getBookmarksFromFolder(null,true),false);
      subscriber.onNext(mBookmarkAdapter);
    }
  }
);
}


Code After:
private Observable<BookmarkViewAdapter> initBookmarkManager(){
  return Observable.create(new Action<BookmarkViewAdapter>(){
    @Override public void onSubscribe(    @NonNull Subscriber<BookmarkViewAdapter> subscriber){
      Context context=getContext();
      if (context != null) {
        mBookmarkAdapter=new BookmarkViewAdapter(getContext(),mBookmarks);
        setBookmarkDataSet(mBookmarkManager.getBookmarksFromFolder(null,true),false);
        subscriber.onNext(mBookmarkAdapter);
      }
      subscriber.onComplete();
    }
  }
);
}


Code Deletions:
                mBookmarkAdapter = new BookmarkViewAdapter(getContext(), mBookmarks);
                setBookmarkDataSet(mBookmarkManager.getBookmarksFromFolder(null, true), false);
                subscriber.onNext(mBookmarkAdapter);


Code Additions:
                Context context = getContext();
                if (context != null) {
                    mBookmarkAdapter = new BookmarkViewAdapter(getContext(), mBookmarks);
                    setBookmarkDataSet(mBookmarkManager.getBookmarksFromFolder(null, true), false);
                    subscriber.onNext(mBookmarkAdapter);
                }
                subscriber.onComplete();

"""
