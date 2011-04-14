# -*- mode: ruby -*-
# The builders make a lot of assumptions about how things are
# configured. For example, we assume your sdist (sources) are in
# ./dist/ and that if the sources are missing they can be created by
# running the python setuptools 'sdist' command. This class provides a
# good base class though and subclassing is fairly easy to make this
# fit any specific needs.

class Builder
  @rpm_build_command = ""
  def initialize(package_name, version, mock_chroot, build_target)
    @package_name = package_name
    @version = version
    @full_name = "#{@package_name}-#{@version}"
    @mock_chroot = mock_chroot
    @build_target = build_target
    @srpm_path = "/var/lib/mock/#{@mock_chroot}/result"
    @sdist = "dist/#{@full_name}.tar.gz"
    @specfile = "#{@package_name}.spec"
    @srpm = nil
  end

  def setup_sdist
    `./setup.py sdist`
  end

  def build_srpm
    build_command = "mock -q -r #{@mock_chroot} --buildsrpm --sources #{@sdist} --spec #{@specfile}"

    self.setup_sdist unless File.exists? @sdist

    puts "|-------------------------------------------------------------|"
    puts "| BUILDING SRPM for #{@mock_chroot} with this command:"
    puts "|    #{build_command}"
    puts "|-------------------------------------------------------------|"

    `#{build_command}`
    
    # Do a check here so we can return something useful.
    result_glob = "#{@srpm_path}/#{@full_name}*.src.rpm"
    results = Dir[result_glob]
    if results.count == 0
      puts "|-------------------------------------------------------------|"
      puts "| ERROR: Could not build srpm for #{@mock_chroot}."
      puts "| Not going to attempt to build RPM."
      puts "| Logs for this failed build are in #{@srpm_path}"
      puts "|-------------------------------------------------------------|"
      return nil
    else
      return true
    end
  end

  def build_rpm
    # There is probably a better way to do this
    result_glob = "#{@srpm_path}/#{@full_name}*.src.rpm"
    results = Dir[result_glob]
    
    if results.first.nil?
      # nil happens when the source RPM couldn't be built. Bail
      # out. Bail out now!
      return nil
    else
      @srpm = results.first
    end

    build_command = "#{@rpm_build_command} build --nowait --noprogress --scratch #{@build_target} #{@srpm}"
    puts "|-------------------------------------------------------------|"
    puts "| BUILDING RPM for #{@mock_chroot} with this command:"
    puts "|    #{build_command}"
    puts "|-------------------------------------------------------------|"

    task_id = nil
    status_url = nil

    # Instead of the normal `backtick` command execution we're using
    # IO.popen here because it's the simplest way to actually the
    # stdout and stderr output from Koji.
    IO.popen(build_command) do |build_process|
      # Iterate over each line of Koji output. Koji doesn't seem to
      # flush it's stderr often so this will not be a continuous
      # flow. That doesn't matter very much anyway.
      build_process.each do |line|
        # Get the info so we can consolidate and report it
        if line.scan(/(Created).*?([0-9]+)/).count > 0
          task_id = line.scan(/(Created).*?([0-9]+)/)[0][1]
        elsif line.scan(/http.*$/).count > 0
          status_url = line.match(/http.*$/)[0]
        else
          puts line
        end
      end
    end

    puts "|-------------------------------------------------------------|"
    puts "| KOJI JOB SUBMITTED. Building with task id: #{task_id}"
    puts "| Track the progress of this build at this url:"
    puts "|    #{status_url}"
    puts "|-------------------------------------------------------------|"
  end

  def srpm
    @srpm
  end

  def to_s
    name_ver = "#{@package_name} (#{@version})\n"
    name_ver << "Build target: #{@build_target}"
  end
end


class BrewBuilder < Builder
  def initialize(package_name, version, mock_chroot, build_target)
    super(package_name, version, mock_chroot, build_target)
    @rpm_build_command = "brew"
  end
end


class KojiBuilder < Builder
  def initialize(package_name, version, mock_chroot, build_target)
    super(package_name, version, mock_chroot, build_target)
    @rpm_build_command = "koji"
  end
end
