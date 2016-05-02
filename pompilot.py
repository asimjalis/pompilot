#!/usr/bin/env python 

'''
Generates pom.xml file with dependencies and creates Java project directory structure.
'''

import sys, re, os

def dep_to_xml(dep):
    dep_parts = re.split(r'[:,]',dep)
    xml = '<dependency>\n'
    for i in xrange(len(dep_parts)):
        if   i == 0: name='groupId'   ; value=dep_parts[i]
        elif i == 1: name='artifactId'; value=dep_parts[i]
        elif i == 2: name='version'   ; value=dep_parts[i]
        else: name,value=re.split('=',dep_parts[i])
        xml += '  <{0}>{1}</{0}>\n'.format(name,value)
    xml += '</dependency>\n'
    return xml

def test_dep_to_xml():
    actual   = dep_to_xml('a:b:c,scope=foo,blah=bar')
    expected = \
    '<dependency>\n' + \
    '  <groupId>a</groupId>\n' + \
    '  <artifactId>b</artifactId>\n' + \
    '  <version>c</version>\n' + \
    '  <scope>foo</scope>\n' + \
    '  <blah>bar</blah>\n' + \
    '</dependency>\n'
    assert expected == actual

def left_pad(spaces,text):
    return spaces + re.sub('\n','\n' + spaces,text.rstrip()) + '\n'
            
def test_left_pad():
    text = 'hello world\n' + 'this is the second line\n'
    actual = left_pad('  ', text)
    expected = '  hello world\n' + '  this is the second line\n'
    assert expected == actual

def xml_wrap(tag,inner_xml):
    xml = ''
    xml += "<" + tag + ">\n"
    xml += left_pad('  ',inner_xml)
    xml += "</" + tag + ">\n"
    return xml

def deps_to_xml(deps):
    xml = ''
    for dep in deps:
        xml += dep_to_xml(dep)
    return xml_wrap('dependencies',xml) 

def arg_to_name_value(arg):
    # Match --k=v
    match = re.match(r'--([^=]+)=(.+)$',arg)
    if match: 
        name,value = match.groups()
        return name,value
    # Match --no-k
    match = re.match(r'--no-([^=]+)$',arg)
    if match: 
        name,value = match.groups()[0],"False"
        return name,value
    # Match --k
    match = re.match(r'--([^=]+)$',arg)
    if match: 
        name,value = match.groups()[0],"True"
        return name,value
    return None,None

def argv_to_options_args(argv):
    options = {}
    args = []
    for arg in argv:
        name,value = arg_to_name_value(arg)
        if name != None:
            options[name] = value
        else:
            args.append(arg)
    return options,args

def test_argv_to_options_args():
    argv = ['file0','--k1=v1','--k2','file1','--no-k3','file2']
    expected_options = { 'k1':'v1','k2':'True','k3':'False' }
    expected_args   = ['file0','file1','file2']
    options,args = argv_to_options_args(argv)
    print args
    assert expected_args    == args
    assert expected_options == options

class Options:
    def __init__(self,argv):
        self.options,self.args = argv_to_options_args(argv)
        self.used_names = set()
    def get(self,name,default_value):
        if name in self.options:
            self.used_names.add(name)
            return self.options[name]
        return default_value
    def get_boolean(self,name,default_value):
        value = self.get(name,default_value)
        return value == 'True'
    def unused_names(self):
        option_names = set(self.options.keys())
        return option_names - used_names
    
def to_pom_xml(group_id,artifact_id,version,deps,jdk):
    deps_xml = deps_to_xml(deps)
    deps_xml = left_pad('  ',deps_xml)
    return POM_XML.format(
        group_id=group_id,
        artifact_id=artifact_id,
        version=version,
        jdk=jdk,
        deps_xml=deps_xml)

def str_to_file(text,path):
    path_dir = os.path.dirname(path)
    os.makedirs(path_dir)
    with open(path,'wb') as f:
        f.write(text)

def main(argv):
    if len(argv) < 3 or argv[1] in ['--help','--h']:
        print USAGE,
        exit(1)

    try:
        options     = Options(argv)
        script      = options.args[0]
        project_name= options.args[1]

        group_id    = project_name
        artifact_id = project_name
        version     = '1.0-SNAPSHOT'
        deps        = options.args[2:]
        jdk         = options.get('jdk','1.7')
        debug       = options.get_boolean('debug', False)

        # Validate project name
        if re.search(r'[^-\w]', project_name):
            error = 'Project name must have letters, numbers or dash'
            raise Exception(error)

        pom_xml     = to_pom_xml(group_id,artifact_id,version,deps,jdk)
        root        = project_name

        pom_path    = os.path.join(root,'pom.xml')
        str_to_file(pom_xml,pom_path)

        package_path = project_name.lower()
        package_path = re.sub(r'[-]', '/', package_path)
        package_name = package_path.replace("/",".")

        java_main_path = os.path.join(root,'src/main/java',
            package_path,'App.java')
        java_test_path = os.path.join(root,'src/test/java',
            package_path,'AppTest.java')
        log4j_path = os.path.join(root,'src/main/resources',
            'log4j.properties')

        import_line = IMPORT_LINE.format(package_name=package_name)
        java_main_text = import_line + JAVA_MAIN
        java_test_text = import_line + JAVA_TEST

        str_to_file(java_main_text, java_main_path)
        str_to_file(java_test_text, java_test_path)
        str_to_file(LOG4J, log4j_path)

    except: 
        print "Error: " + str(sys.exc_info()[1])
        if debug:
            print "Trace: "
            raise 
        else:
            exit(1)

LOG4J=r'''\
log4j.rootLogger=INFO, stdout
log4j.appender.stdout=org.apache.log4j.ConsoleAppender
log4j.appender.stdout.Target=System.out
log4j.appender.stdout.layout=org.apache.log4j.PatternLayout
log4j.appender.stdout.layout.ConversionPattern=%d{yy/MM/dd HH:mm:ss} %p %c{2}: %m%n
'''

IMPORT_LINE='''\
package {package_name};
'''

JAVA_MAIN='''\

public class App {
    public static void main(String[] args) throws Exception {
        System.out.println("Hello, world!");
    }
}
'''

JAVA_TEST='''\

import org.junit.*;

import static org.junit.Assert.assertEquals;

public class AppTest {
    @Test
    public void basic() throws Exception {
        assertEquals(1,1);
    }
}
'''


POM_XML = '''\
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <groupId>{group_id}</groupId>
  <artifactId>{artifact_id}</artifactId>
  <version>{version}</version>
  <packaging>jar</packaging>

  <name>{artifact_id}</name>
  <url>http://maven.apache.org</url>

  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  </properties>

  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.3</version>
        <configuration>
          <source>{jdk}</source>
          <target>{jdk}</target>
        </configuration>
      </plugin>
    </plugins>
  </build>

{deps_xml}
</project>
'''

USAGE='''\

POM Pilot
=========

Overview
--------

Generates pom.xml file with dependencies and creates Java project
directory structure.

Usage
-----

    pompilot.py [options] project-name dependency1 [dependencies]

Options
-------

    --jdk=1.8   Emit code for Java 1.8 (default)
    --jdk=1.7   Emit code for Java 1.7
    --debug     Print stack trace on error

Examples
--------

Example 1: Generate project pom.xml has JUnit dependency in test scope

    pompilot.py linux-lab1 junit:junit:4.12:scope=test

Example 2: pom.xml for Hadoop app

    pompilot.py mapreduce-lab2 \
        org.apache.hadoop:hadoop-aws:2.7.1 \
        org.apache.hadoop:hadoop-client:2.7.1 \
        com.amazonaws:aws-java-sdk-s3:1.10.30 \
        org.apache.mrunit:mrunit:1.1.0:classifier=hadoop2:scope=test \
        junit:junit:4.12:scope=test

Install
-------

    curl -LO https://raw.githubusercontent.com/asimjalis/pompilot/master/pompilot.py
    chmod 755 pompilot.py
    mv ~/pompilot.py ~/bin/.
'''

if __name__ == '__main__':
    main(sys.argv)
        

