def gitUrl = 'https://github.com/isacssouza/immutable-infrastructure.git'

job('api') {
    scm {
        git {
            remote {
                url(gitUrl)
            }
            extensions {
                cleanBeforeCheckout()
            }
        }
    }
    steps {
        shell('cd api; ./mvnw -e clean test')
    }
    publishers {
        archiveArtifacts('**/target/*.jar')
        archiveJunit('**/target/**/TEST*.xml') {
            allowEmptyResults(false)
            retainLongStdout()
            testDataPublishers {
                publishTestStabilityData()
            }
        }
    }
}