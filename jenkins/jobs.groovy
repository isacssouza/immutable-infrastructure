def gitUrl = 'git://github.com/isacssouza/immutable-infrastructure.git'

job('api') {
    scm {
        git(gitUrl)
    }
    steps {
        maven('-e clean test')
    }
}