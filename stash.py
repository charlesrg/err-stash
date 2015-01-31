from errbot import BotPlugin, botcmd, webhook
import logging
import json

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

## Author: Charles Gomes (github.com/charlesrg)
## LICENSE: GPL


def logReturn(message):
    logging.warning(message)
    return message

contacts = {'project': 'root@chat.server.tld', 'coolProject': 'coolGuys@chat.server.tld'}
DEFAULT_CONFIG = { 'contacts': contacts }

class stash(BotPlugin):
    """Stash Plugin for Err"""
    min_err_version = '2.1.0'

    @botcmd
    def get_configuration_template(self):
        return DEFAULT_CONFIG

    def check_configuration(self, configuration):
        """Bypass config check as err will fail without it"""
        pass

    def stash_help(self, *args):
        """Stash plugin Help."""
        message=[]
        message.append('Simple Stash commit notification plugin.')
        message.append('To configure who gets notified when a project gets a commit.')
        message.append('Send: config stash {\'contacts\': { \'project\': \'room@chat.server.tld\', \'coolProject\': \'coolGuys@chat.server.tld\'},} ')
        message.append('')
        message.append('You also need to setup http://stash/projects/NAME/repos/REPONAME/settings/hooks')
        message.append('Post-Receive WebHooks -> http://errbotServer.domain.tld:3141/stash/')
        message.append('')
        message.append('To show the config use: stash config .')
        message.append('To show the config use: stash config .')
        message.append('To reset the config use: stash reset .')
        return '\n'.join(message)

    @botcmd(admin_only=True)
    def stash_config(self, *args):
        """Returns current plugin config."""
        return json.dumps(self.config, indent=4, sort_keys=True)

    @botcmd(admin_only=True)
    def stash_reset(self, *args):
        """Reset the configuration."""
        self.config = DEFAULT_CONFIG
        self.save_config()
        return 'Done. Config reset.'
    
    @webhook
    def stash(self, post):
        if self.config is None:
            return logReturn('Pluging not configured, see stash help')
        if not 'contacts' in self.config:
            return logReturn('config does not have a contacts session')
        contacts = self.config['contacts']

        if post is None:
            return logReturn('Blank')

        if not 'repository' in post:
            return logReturn('missing repository info')
        if not 'project' in post['repository']:
            return logReturn('missing repository key')
        if not 'name' in post['repository']['project']:
            return logReturn('missing project name')

        project=post['repository']['project']['name']

        if not project in contacts:
            return logReturn('no room to notify about this commit')

        room=contacts[project]
        repo=post['repository']['name']

        if not 'refChanges' in post:
            return logReturn('missing change refChanges')
        if len(post['refChanges'])  < 1:
            return logReturn('missing refChanges index')
        if not 'type' in post['refChanges'][0]:
            return logReturn('missing change type')

        changeType=post['refChanges'][0]['type']

        if not 'changesets' in post:
            return logReturn('missing changesets')
        if not 'values' in  post['changesets']:
            return logReturn('missing commit key')
        if len(post['changesets']['values'])  < 1:
            return logReturn('missing changesets values array')
        if not 'toCommit' in post['changesets']['values'][0]:
            return logReturn('missing commit key')
        if not 'author' in post['changesets']['values'][0]['toCommit']:
            return logReturn('missing commit author key')
        if not 'name' in post['changesets']['values'][0]['toCommit']['author']:
            return logReturn('missing commit author key')

        author=post['changesets']['values'][0]['toCommit']['author']['name'].split(' ')[0].title()

        if not 'message' in  post['changesets']['values'][0]['toCommit']:
            return logReturn('missing commit message')

        message=post['changesets']['values'][0]['toCommit']['message']

        self.send(room,'Git Commit: ' + project + '/' + repo + ' - ' + author + ' ('+ changeType + ') : ' + message , message_type="groupchat")
        return "OK"
