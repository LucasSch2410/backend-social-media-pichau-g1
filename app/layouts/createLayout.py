from fastapi import status
from fastapi.responses import JSONResponse

from .wide.wide_layout import wideLayout
from .stories.stories_layout import storiesLayout
from .post.post_layout import postLayout
from .push.push_layout import pushLayout

def createLayout(typeSocial):
    if typeSocial == "stories":
        return storiesLayout
    elif typeSocial == "wide":
        return wideLayout
    elif typeSocial == "push":
        return pushLayout
    elif typeSocial == "post":
        return postLayout
