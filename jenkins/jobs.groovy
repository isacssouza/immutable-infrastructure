def gitUrl = 'https://github.com/isacssouza/immutable-infrastructure.git'

apiBuildNumberParam = 'API_BUILD_NUMBER'

apiBuildName = 'build-api'
job(apiBuildName) {
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
        shell('cd api; ./mvnw -e --batch-mode -T2C clean install')
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

job(bakeJobName) {
    parameters {
        stringParam(apiBuildNumberParam, null, 'Api build number to get the artifacts from')
    }
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
        copyArtifacts(apiBuildName) {
            buildSelector {
                buildNumber("\$${apiBuildNumberParam}")
            }
            optional(false)
        }
        shell("cd packer; packer build api.json")
    }
    publishers {
        archiveArtifacts {
            pattern('packer/*.tar')
            onlyIfSuccessful()
        }
    }
}
