from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.encoding import force_text
from diff_match_patch import diff_match_patch
import json, urllib
def getpage(pagen, qlist, noi):
    paginator = Paginator(qlist, noi)
    try:
        items = paginator.page(pagen)
    except (EmptyPage, PageNotAnInteger):
        items = paginator.page(1)
    return items
    
def recaptcha(request, secret):
    values = {
        'secret': secret,
        'response': request.POST.get('g-recaptcha-response')
    }
    data = urllib.parse.urlencode(values).encode()
    ureq =  urllib.request.Request('https://www.google.com/recaptcha/api/siteverify', data=data)
    response = urllib.request.urlopen(ureq)
    return json.loads(response.read().decode())

class Pages:

    def __init__(self, objects, count):
        self.pages = Paginator(objects, count)

    def pages_to_show(self, page):
        # pages_wanted stores the pages we want to see, e.g.
        #  - first and second page always
        #  - two pages before selected page
        #  - the selected page
        #  - two pages after selected page
        #  - last two pages always
        #
        # Turning the pages into a set removes duplicates for edge
        # cases where the "context pages" (before and after the
        # selected) overlap with the "always show" pages.
        pages_wanted = set([1,2,
                            page-2, page-1,
                            page,
                            page+1, page+2,
                            self.pages.num_pages-1, self.pages.num_pages])

        # The intersection with the page_range trims off the invalid
        # pages outside the total number of pages we actually have.
        # Note that includes invalid negative and >page_range "context
        # pages" which we added above.
        pages_to_show = set(self.pages.page_range).intersection(pages_wanted)
        pages_to_show = sorted(pages_to_show)

        # skip_pages will keep a list of page numbers from
        # pages_to_show that should have a skip-marker inserted
        # after them.  For flexibility this is done by looking for
        # anywhere in the list that doesn't increment by 1 over the
        # last entry.
        skip_pages = [ x[1] for x in zip(pages_to_show[:-1],
                                         pages_to_show[1:])
                       if (x[1] - x[0] != 1) ]

        # Each page in skip_pages should be follwed by a skip-marker
        # sentinel (e.g. -1).
        for i in skip_pages:
            pages_to_show.insert(pages_to_show.index(i), -1)

        return pages_to_show
        
dmp = diff_match_patch()

def generate_diffs(old_version, new_version, field_name, cleanup):
    """Generates a diff array for the named field between the two versions."""
    # Extract the text from the versions.
    old_text = old_version.field_dict[field_name] or ""
    new_text = new_version.field_dict[field_name] or ""
    # Generate the patch.
    diffs = dmp.diff_main(force_text(old_text), force_text(new_text))
    if cleanup == "semantic":
        dmp.diff_cleanupSemantic(diffs)
    elif cleanup == "efficiency":
        dmp.diff_cleanupEfficiency(diffs)
    elif cleanup is None:
        pass
    else:
        raise ValueError("cleanup parameter should be one of 'semantic', 'efficiency' or None.")
    return diffs

def generate_patch(old_version, new_version, field_name, cleanup=None):
    """
    Generates a text patch of the named field between the two versions.
    
    The cleanup parameter can be None, "semantic" or "efficiency" to clean up the diff
    for greater human readibility.
    """
    diffs = generate_diffs(old_version, new_version, field_name, cleanup)
    patch = dmp.patch_make(diffs)
    return dmp.patch_toText(patch)

def generate_patch_html(old_version, new_version, field_name, cleanup=None):
    """
    Generates a pretty html version of the differences between the named 
    field in two versions.
    
    The cleanup parameter can be None, "semantic" or "efficiency" to clean up the diff
    for greater human readibility.
    """
    diffs = generate_diffs(old_version, new_version, field_name, cleanup)
    return dmp.diff_prettyHtml(diffs)
class newdiff(diff_match_patch):
    def diff_prettyHtml(self, diffs):
        """Convert a diff array into a pretty HTML report.
        Args:
          diffs: Array of diff tuples.
        Returns:
          HTML representation.
        """
        html = []
        for (op, text) in diffs:
          if op == self.DIFF_INSERT:
            html.append("<ins>%s</ins>" % text)
          elif op == self.DIFF_DELETE:
            html.append("<del>%s</del>" % text)
          elif op == self.DIFF_EQUAL:
            html.append("<span>%s</span>" % text)
        print ("".join(html))
        return "".join(html)