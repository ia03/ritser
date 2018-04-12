from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.encoding import force_text
from diff_match_patch import diff_match_patch
from django.db.models import Q
from django import forms
from .models import Topic, Debate, Argument
from accounts.models import User
from django.utils import timezone


def debateslist(topic):
    if (topic.slvl == 0) or (topic.slvl == 1):
        return topic.debates.filter(Q(approvalstatus=0) | Q(approvalstatus=1))
    else:
        return topic.debates.filter(approvalstatus=0)


def getpage(pagen, qlist, noi):
    paginator = Paginator(qlist, noi)
    try:
        items = paginator.page(pagen)
    except (EmptyPage, PageNotAnInteger):
        items = paginator.page(1)
    return items


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
        pages_wanted = set([1, 2,
                            page - 2, page - 1,
                            page,
                            page + 1, page + 2,
                            self.pages.num_pages - 1, self.pages.num_pages])

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
        skip_pages = [x[1] for x in zip(pages_to_show[:-1],
                                        pages_to_show[1:])
                      if (x[1] - x[0] != 1)]

        # Each page in skip_pages should be follwed by a skip-marker
        # sentinel (e.g. -1).
        for i in skip_pages:
            pages_to_show.insert(pages_to_show.index(i), -1)

        return pages_to_show


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
        raise ValueError(
            "cleanup parameter should be one of 'semantic', 'efficiency' or None.")
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
        return "".join(html)


dmp = newdiff()


def htmldiffs(original, new):
    diffs = dmp.diff_main(original, new)
    dmp.diff_cleanupSemantic(diffs)
    return dmp.diff_prettyHtml(diffs)



# form utility functions


def chkdeb(did):
    try:
        return Debate.objects.get(id=did)
    except Debate.DoesNotExist:
        raise forms.ValidationError(
            'Debate %(debate_id)s not found.',
            code='debatenotfound',
            params={
                'debate_id': did})
def chktop(tname):
    try:
        return Topic.objects.get(name=tname)
    except Topic.DoesNotExist:
        raise forms.ValidationError(
            'Topic %(tname)s not found.',
            code='topicnotfound',
            params={
                'tname': tname})

def chkusr(uname):
    try:
        return User.objects.get(username=uname)
    except User.DoesNotExist:
        raise forms.ValidationError(
            'User %(uname)s not found.',
            code='usernotfound',
            params={
                'uname': uname})

def disablefield(instance, *args):
    for arg in args:
        instance.fields[arg].required = False
        instance.fields[arg].widget = forms.HiddenInput()


def donotrequire(instance, *args):
    for arg in args:
        instance.fields[arg].required = False


def cleanownername(instance):
    data = instance.cleaned_data['owner_name']
    if instance.edit != 0:
        try:
            owner = User.objects.get(username=data)
        except User.DoesNotExist:
            raise forms.ValidationError(
                'User %(owner_name)s not found.',
                code='usernotfound',
                params={
                    'owner_name': data})
        if not owner.is_active:
            raise forms.ValidationError(
                'User %(owner_name)s can not be set as the owner.',
                code='userinactive',
                params={
                    'owner_name': data})
    return data


def cleanowner(instance):
    if instance.edit == 0:
        return instance.user
    else:
        return instance.cleaned_data.get('owner')


def cleancreatedon(instance):
    if instance.edit == 0:
        return timezone.now()
    else:
        return instance.instance.created_on


def cleanapprovalstatus(instance):
    if instance.edit == 0:
        return 1
    elif instance.edit == 1:
        return instance.instance.approvalstatus
    elif instance.edit == 2:
        data = instance.cleaned_data.get('approvalstatus')
        if data not in [0, 1, 2]:
            raise forms.ValidationError(
                'Invalid approval status setting %(approved_status)s, must be 0, 1, or 2.',
                code='invalidapprovalstatus',
                params={
                    'approved_status': data})
        return data


def cleaneditedon(instance):
    return timezone.now()


def cleanmodnote(instance):
    if instance.edit == 0:
        return ""
    elif instance.edit == 1:
        return instance.instance.modnote
    elif instance.edit == 2:
        return instance.cleaned_data.get('modnote')


def setapprovedon(instance):
    cleaned_data = instance.cleaned_data
    if (instance.edit == 2 and instance.instance.approvalstatus ==
            1 and cleaned_data.get('approvalstatus') != 1):
        return timezone.now()
    elif instance.edit == 1:
        return instance.instance.approved_on
    elif instance.edit == 0:
        return None

def cleandslvl(data):
    if data not in [0, 1, 2, 3, 4]:
        raise forms.ValidationError(
            'Invalid security level setting %(slvl)s, must be 0, 1, 2, 3 or 4.',
            code='invalidslvl',
            params={
                'slvl': data})