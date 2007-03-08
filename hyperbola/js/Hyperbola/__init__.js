// import Nevow.Athena
// import Mantissa.LiveForm
// import Mantissa.AutoComplete

Hyperbola._ReloadingFormWidget = Mantissa.LiveForm.FormWidget.subclass('Hyperbola._ReloadingFormWidget');
Hyperbola._ReloadingFormWidget.methods(
    function submitSuccess(self, result) {
        var D = Hyperbola._ReloadingFormWidget.upcall(
            self, 'submitSuccess', result);
        D.addCallback(
            function(ignored) {
                self._submittedSuccessfully();
            });
        return D;
    },

    function _submittedSuccessfully(self) {
        document.location.reload();
    });

Hyperbola.AddBlog = Hyperbola._ReloadingFormWidget.subclass('Hyperbola.AddBlog');
Hyperbola.AddComment = Hyperbola._ReloadingFormWidget.subclass('Hyperbola.AddComment');

Hyperbola.BlogPostBlurbController = Nevow.Athena.Widget.subclass('Hyperbola.BlogPostBlurbController');
Hyperbola.BlogPostBlurbController.methods(
    function togglePostComments(self) {
        var node = self.firstNodeByAttribute(
            'class', 'hyperbola-blog-post-comments');
        if(node.style.display == '') {
            node.style.display = 'none';
        } else {
            node.style.display = '';
        }
        return false;
    },

    /**
     * Toggle the visibility of the 'edit post' form
     */
    function toggleEditForm(self) {
        var node = self.firstNodeByAttribute(
            'athena:class', 'Hyperbola.BlogPostBlurbEditorController');
        if(node.style.display == '') {
            node.style.display = 'none';
        } else {
            node.style.display = '';
        }
        return false;
    },

    /**
     * Tell the server to do delete this post, and reload the page
     */
    function deletePost(self) {
        var result = self.callRemote('delete');
        result.addCallback(
            function(ignored) {
                document.location.reload();
            });
        return false;
    });

Hyperbola.BlogBlurbController = Nevow.Athena.Widget.subclass('Hyperbola.BlogBlurbController');
Hyperbola.BlogBlurbController.methods(
    function chooseTag(self, node) {
        var tag = node.firstChild.nodeValue,
            form = self.firstNodeByAttribute(
                'name', 'tag-form');
        form.tag.value = tag;
        form.submit();
        return false;
    },

    function unchooseTag(self) {
        var form = self.firstNodeByAttribute('name', 'tag-form');
        form.tag.value = '';
        form.submit();
        return false;
    });

Hyperbola.AddBlogPost = Hyperbola._ReloadingFormWidget.subclass('Hyperbola.AddBlogPost');
Hyperbola.AddBlogPost.methods(
    function __init__(self, node, allTags) {
        Hyperbola.AddBlogPost.upcall(self, '__init__', node);
        self.autoComplete = Mantissa.AutoComplete.Controller(
            Mantissa.AutoComplete.Model(allTags),
            Mantissa.AutoComplete.View(
                self.firstNodeByAttribute('name', 'tags'),
                self.firstNodeByAttribute(
                    'class', 'hyperbola-tag-completions')));
    },

    function togglePostForm(self) {
        var node = self.firstNodeByAttribute(
            'class', 'hyperbola-add-post-form');
        if(node.style.display == '') {
            node.style.display = 'none';
        } else {
            node.style.display = '';
            document.documentElement.scrollTop = document.documentElement.scrollHeight;
        }
        return false;
    });

Hyperbola.AddBlogPostDialog = Hyperbola.AddBlogPost.subclass('Hyperbola.AddBlogPostDialog');
Hyperbola.AddBlogPostDialog.methods(
    function submit(self) {
        Hyperbola.AddBlogPostDialog.upcall(self, 'submit');
        window.close();
    });

Hyperbola.BlogPostBlurbEditorController = Hyperbola._ReloadingFormWidget.subclass('Hyperbola.BlogPostBlurbEditorController');
/**
 * Code for responding to events related to editing of blog post blurbs
 */
Hyperbola.BlogPostBlurbEditorController.methods(
    /**
     * Hide the 'edit blog post' form
     */
    function hideEditForm(self) {
        self.node.style.display = 'none';
        return false;
    });
