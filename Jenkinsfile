#!groovy

// ------------------------------------------------------------------------
//  \\//
//   \/aporIO - Synse Server.
//
//  Jenkinsfile for the synse-server repo.
//
// ------------------------------------------------------------------------

def vaporWareGitOrgUrl = 'http://github.com/vapor-ware/'

// Output the Jenkins job parameters at the top of the output so that
// we can tell what we're testing.
// TODO: Could rename below to synse_server_internal, but this is all going away.
def displayParameters() {
    echo("Jenkins job parameters:")
    echo("synse_server_branch: ${synse_server_branch}")
}

// Get repo source from git into a directory with the same name as the repo
// and checkout the given branch.
def getSource(repoName, repoUrl, branchName) {
    sh("echo getSource ${repoName}, ${repoUrl}, ${branchName}.")
    sh("echo PWD initially is ${PWD}.")
    sh("ls")
    // Each repo needs its own directory.
    // Clean it out every time.
    sh("rm -rf ${repoName}")
    sh("mkdir ${repoName}")
    dir(repoName) {
        sh("echo PWD before git is ${PWD}")
        git credentialsId: '921e6165-d375-4f67-b608-2fd9809bae9a', url: repoUrl
        // Things failed when I tried to put the branch in the git command above.
        sh("echo PWD after git is ${PWD}.")
        sh("git checkout ${branchName}")
        sh("git log -n 1") // Show the commit we are on.
    }
}

// Build and test the repo/branch.
// makefileDirectory is the relative path to the test makefile.
// makeCommandLins is the make command line to run the tests with.
def buildAndTest(repoName, branch, makefileDirectory, makeCommandLine) {
    echo("Testing ${repoName} branch ${branch}.")
    dir(makefileDirectory) {
        sh("echo PWD for testing is ${PWD}.")
        sh("git branch") // paranoid check (The branch is fine.)
        sh("git log -n 1") // Show the commit we are testing.
        sh(makeCommandLine)
    }
}

// Remove all docker images and containers.
def cleanupDocker() {
    echo('Clean up any lingering containers or images.')
    sh('docker rm $(docker ps -aq) -f || true')
    sh('docker ps -a')
    sh('docker rmi $(docker images -aq) -f || true')
    sh('docker images -a')
}

node {
    stage('Display Parameters') {
        displayParameters()
    }

    stage('Getting synse-server-internal') {

        getSource('synse-server-internal', vaporWareGitOrgUrl + 'synse-server-internal',
            synse_server_branch)
    }

    stage('Build and test synse-server-internal') {
        try {
            cleanupDocker()

            // TEMP: build the synse-server-internal image - since it currently doesn't
            // exit in dockerhub and is required by the graphql tests, we need
            // to build it locally.
            buildAndTest('synse-server-internal', synse_server_branch,
                'synse-server-internal', 'make build')

            // Test graphql.
            // # Broken #229
            // buildAndTest('synse-server', synse_server_branch,
            //    'synse-server', 'make graphql-test')

            // Test the backend.
            buildAndTest('synse-server-internal', synse_server_branch,
                'synse-server-internal/synse/tests/', 'make test-x64')
        } finally {
            echo('Cleaning up.')
            cleanupDocker()
        }
    }
}
