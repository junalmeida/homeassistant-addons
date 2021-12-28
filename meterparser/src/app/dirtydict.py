class DirtyDict(dict):
  """
  DirtyDict behaves (hopefully) like a regular dict but overrides mutator
  methods to mark the dictionary dirty.  In this way changes to the data are
  tracked in order to, for example, keep related database objects in sync.
  """

  def __init__(self, *args, **kwargs):
    self._dirty = False
    self._created = []
    self._updated = []
    self._deleted = []
    super().__init__(*args, **kwargs)

  def __delitem__(self, key):
    self._dirty = True
    self._deleted.append(key)
    super().__delitem__(key)

  def __setitem__(self, key, value):
    self._dirty = True
    if key in self.keys():
      self._updated.append(key)
    else:
      self._created.append(key)
    super().__setitem__(key, value)

  def clear(self):
    self._dirty = True
    self._deleted.extend(self.keys())
    super().clear()

  def pop(self, key, default=None):
    self._dirty = True
    if key in self.keys():
      self._deleted.append(key)
    return super().pop(key, default)

  def popitem(self):
    self._dirty = True
    popped = super().popitem()
    self._deleted.append(popped[0])
    return popped
  def setdefault(self, key, default=None):
    if key not in self.keys():
      self._dirty = True
      self._created.append(key)
    return super().setdefault(key, default)

  def update(self, other):
    self._dirty = True
    for key in other.keys():
      if key in self.keys():
        self._updated.append(key)
      else:
        self._created.append(key)
    super().update(other)

  @property
  def dirty(self):
    return self._dirty

  @dirty.setter
  def dirty(self, value):
    self._dirty = value
    if value == True:
      self._created.clear()
      self._updated.clear()
      self._deleted.clear()

  @property
  def created(self):
    return self._created

  @property
  def updated(self):
    return self._updated

  @property
  def deleted(self):
    return self._deleted