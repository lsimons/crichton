#!/usr/bin/env ruby

# Use the Puppet::Parser to read a .pp file containing one class,
#     change the package data for that class, then write it back out.
# Note the file will get reformatted (i.e. whitespace changes) if it
#     is not in the expected format yet.
#
# Usage:
#   upgrading two packages
#   ./edit_manifest_package.rb pal pal.pp pal-foo=1.0.0 pal-bar=2.1.2
#
#   upgrading a package to 'latest' works too
#   ./edit_manifest_package.rb pal pal.pp pal-foo=latest
#
#   adding a new package
#   ./edit_manifest_package.rb pal pal.pp pal-new-package=1.0.0

require 'puppet/parser'

def code_to_str(code, versions, seen_packages)
  result = ""
  if code.class == Puppet::Parser::AST::ASTArray
    code.each { |child_code|
      result += code_to_str(child_code, versions, seen_packages=seen_packages)
    }
  elsif code.class == Puppet::Parser::AST::Resource
    if code.title.class != Puppet::Parser::AST::ASTArray:
      title = code.title.to_s
      if title.start_with? '"' or title.start_with? "'"
        title = title[1..-1]
      end
      if title.end_with? '"' or title.end_with? "'"
        title = title[0..-2]
      end
      seen_packages.push title
    elsif code.type == "package":
      raise "Found some kind of construct like package { ['foo', 'bar']: blah} which we don't support for packages"
    end
    
    if code.doc and code.doc != ""
      result += "  # " + code.doc
      if not code.doc.end_with? "\n"
        result += "\n"
      end
    end
    result += "  #{code.type} { #{code.title}: "
    code.parameters.each { |parameter|
      if code.type == "package" and parameter.param == "ensure" and versions.has_key? title
        result += "ensure => \"#{versions[title]}\", "
      else
        parameter_s = parameter.to_s
        result += "#{parameter_s}, "
      end
    }
    result = result[0..-3]
    result += " }\n"
  else
    raise "Cannot handle AST type #{code.class}"
  end
  return result
end

def main(classname, manifest, versions, env="production")
  p = Puppet::Parser::Parser.new env
  
  code = ""
  tcol = p.parse manifest
  tcol.hostclasses.each do |name,c|
    if name != classname
      raise "Expected file with only one class named '#{classname}', found #{name}"
    end
    
    code += "class #{classname} "
    if c.parent and c.parent != ""
      code += "inherits #{c.parent} "
    end
    code += "{\n"
    seen_packages=[]
    code += code_to_str(c.code, versions, seen_packages)
    versions.each { |k,v|
      if not seen_packages.include? k
        code += "  package { \"#{k}\": ensure => \"#{v}\" }\n"
      end
    }
    code += "}\n"
  end
  return code
end

if __FILE__ == $0
  classname = ARGV.shift
  fname = ARGV.shift
  file = File.open(fname, "r")
  manifest = file.read
  file.close

  versions = {}
  ARGV.each { |a| 
    k, v = a.split("=", 2)
    versions[k] = v
  }

  manifest = main(classname, manifest, versions)
  file = File.open(fname, "w")
  file.write manifest
  file.close
end
