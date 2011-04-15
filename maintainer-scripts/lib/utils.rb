# -*- mode: ruby -*-

def prepend_all(list, prefix)
  list.map {|item| prefix + item}
end

def prepend_all!(list, prefix)
  list.map! {|item| prefix + item}
end
