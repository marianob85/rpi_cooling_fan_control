properties(
	[
		buildDiscarder(logRotator(artifactDaysToKeepStr: '', artifactNumToKeepStr: '', daysToKeepStr: '', numToKeepStr: '10')),
		pipelineTriggers([pollSCM('0 H(5-6) * * 5')])
	]
)
pipeline
{
	agent none
		options {
		skipDefaultCheckout true
	}
	environment {
		GITHUB_TOKEN = credentials('marianob85-github-jenkins')
		NEXUS_CREDS = credentials('Nexus-Mariano-HTPC')
	}
	stages {
		stage('Create deb'){
			agent{ label "linux/u24.04/base" }
			steps {
 				checkout scm
				script {
					env.GITHUB_REPO = sh(script: 'basename $(git remote get-url origin) .git', returnStdout: true).trim()
				}
				createDeb( "all")
				archiveArtifacts artifacts: '*.deb', onlyIfSuccessful: true,  fingerprint: true
				stash includes: '*.deb', name: 'packages'
			}
		}
		stage('Nexus upload') {
			agent{ label "linux/u24.04/base" }
			when {
				branch 'master'
			}
			steps {
				unstash 'packages'
				sh '''
					for f in *.deb; do
						[ -e "$f" ] || continue
						STATUS=$(curl -s -o /dev/null -w '%{http_code}' --insecure -u ${NEXUS_CREDS_USR}:${NEXUS_CREDS_PSW} -H "Content-Type: multipart/form-nedata" --data-binary @$f ${NEXUS_SERVER}/repository/ubuntu/)
						if [ $STATUS -ne 201 ]; then
							exit $STATUS
						fi
					done		
				'''
			}
		}
		
		stage('Release') {
			when {
				buildingTag()
			}
			agent{ label "linux/u24.04/go:1.20.1" }
			steps {
				unstash 'packages'
				sh '''
					export GOPATH=${PWD}
					go get github.com/github-release/github-release
					bin/github-release release --user marianob85 --repo ${GITHUB_REPO} --tag ${TAG_NAME} --name ${TAG_NAME}
					for filename in *.deb; do
						[ -e "$filename" ] || continue
						basefilename=$(basename "$filename")
						bin/github-release upload --user marianob85 --repo ${GITHUB_REPO} --tag ${TAG_NAME} --name ${basefilename} --file ${filename}
					done
				'''
			}
		}
	}
	post { 
        changed { 
            emailext body: 'Please go to ${env.BUILD_URL}', to: '${DEFAULT_RECIPIENTS}', subject: "Job ${env.JOB_NAME} (${env.BUILD_NUMBER}) ${currentBuild.currentResult}".replaceAll("%2F", "/")
        }
    }
}

def createDeb( arch ) {
	sh """
export TARGET_VER=1.0.0
export TARGET_NAME=fan-control_\$TARGET_VER.${BUILD_NUMBER}_${arch}
export TARGET_DATA_DIR=./\$TARGET_NAME/usr/share/fan-control
export TARGET_SERVICE_DIR=./\$TARGET_NAME/lib/systemd/system
export PACKAGE_NAME=fan-control

mkdir -p \$TARGET_DATA_DIR
mkdir -p \$TARGET_SERVICE_DIR
mkdir ./\$TARGET_NAME/DEBIAN

echo "
Package: \$PACKAGE_NAME
Version: \$TARGET_VER.${BUILD_NUMBER}
Section: base
Priority: optional
Architecture: ${arch}
Depends: python3, python3-dev, python3-venv, python3-systemd, libsystemd-dev, python3-gpiozero
Maintainer: Mariusz Brzeski <marianob85work@gmail.com>
Homepage: manobit.com
Description: Fan control service for raspberryPI" > ./\$TARGET_NAME/DEBIAN/control

cp ./deb/postinst ./deb/postrm ./deb/prerm ./\$TARGET_NAME/DEBIAN
cp ./fanctrl.py ./requirements.txt ./\$TARGET_DATA_DIR
cp ./deb/fan-control.service ./\$TARGET_SERVICE_DIR

dpkg-deb --build --root-owner-group \$TARGET_NAME
dpkg-name -o \$TARGET_NAME.deb
		"""
}
