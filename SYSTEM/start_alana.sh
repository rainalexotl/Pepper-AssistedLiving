#!/bin/sh



if [ -z "$1" ]; then
    echo "Usage: $0 <config.yaml>"; exit 1
fi

#added by me, THECYBERSMITH, to do stuff
pkill gunicorn

python3 -m venv valana
#added by me, THECYBERSMITH, to do stuff

SESSION_NAME="Alana"
BOT_WORKERS=1
HUB_WORKERS=1

#MACOS
#SOURCE="source ~/.bash_profile"

#Linux
#SOURCE="source ~/.bashrc"

# ALANA_PATH and ALANA_ENV should be set 
export ALANA_PATH=bot_ensemble
export ALANA_ENV=valana/bin/activate

cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
tmux has-session -t ${SESSION_NAME}

if [ $? != 0 ]
then
  # Create the session
  tmux new-session -s ${SESSION_NAME} -n Alana -d

  # First window (0) -- Bucket
  tmux send-keys -t ${SESSION_NAME} "source $ALANA_ENV; python alana_main.py --config_file=$1 -cv=critical" C-m
  #https://verboselogs.readthedocs.io/en/latest/readme.html#overview-of-logging-levels VERY IMPORTANT!!!!!!

#  sleep 2

  # Bots (2)
  tmux new-window -n "aiml bots" -t ${SESSION_NAME}:2 
  #tmux send-keys -t ${SESSION_NAME}:2 "source $ALANA_ENV; cd $ALANA_PATH/ProfanityBot; gunicorn --workers=$BOT_WORKERS bot:app --bind 0.0.0.0:5113" C-m
  # tmux split-window -h -t ${SESSION_NAME}:2
  tmux send-keys -t ${SESSION_NAME}:2 "source $ALANA_ENV; cd $ALANA_PATH/aiml_bots; gunicorn --workers=$BOT_WORKERS bot:app --bind 0.0.0.0:5112" C-m
  tmux split-window -v -t ${SESSION_NAME}:2
  tmux send-keys -t ${SESSION_NAME}:2.1 'source $ALANA_ENV; cd $ALANA_PATH/aiml_bots/bots/persona; sh rest.sh' C-m
  tmux split-window -h -t ${SESSION_NAME}:2
  tmux send-keys -t ${SESSION_NAME}:2.2 'source $ALANA_ENV; cd $ALANA_PATH/aiml_bots/bots/rosie_fixed; sh rest.sh' C-m


  # clarification/ontology (3)
  tmux new-window -n "clarification/ontology" -t ${SESSION_NAME}:3 
  tmux send-keys -t ${SESSION_NAME}:3 "source $ALANA_ENV; cd $ALANA_PATH/clarification_bot; gunicorn --workers=${BOT_WORKERS} http_bot:app --bind 0.0.0.0:5111" C-m
  tmux split-window -v -t ${SESSION_NAME}:3
  tmux send-keys -t ${SESSION_NAME}:3.1 "source $ALANA_ENV; cd $ALANA_PATH/ontology_bot; python http_bot.py" C-m

  # coherence(4)
  tmux new-window -n "intro/coherence" -t ${SESSION_NAME}:4 
  tmux send-keys -t ${SESSION_NAME}:4 "source $ALANA_ENV; cd $ALANA_PATH/coherence_bot; gunicorn --workers=${BOT_WORKERS} bot:app --bind 0.0.0.0:5115" C-m

  # evi (5)
  tmux new-window -n "evi" -t ${SESSION_NAME}:5
  tmux send-keys -t ${SESSION_NAME}:5 "source $ALANA_ENV; cd $ALANA_PATH/evibot/; gunicorn --workers=${BOT_WORKERS} bot:app --bind 0.0.0.0:5117" C-m
 
  # wiki (6)
  #tmux new-window -n "wiki" -t ${SESSION_NAME}:6
  #tmux send-keys -t ${SESSION_NAME}:6 "source $ALANA_ENV; cd $ALANA_PATH/wiki_bot_mongo; gunicorn --workers=${BOT_WORKERS} bot:app --bind 0.0.0.0:5222" C-m
 
  # mongodb(6)
  tmux new-window -n "mongodb" -t ${SESSION_NAME}:6
  tmux send-keys -t ${SESSION_NAME}:6 "mongod --dbpath db_data/" C-m

  # NEW_BOT (7)
  tmux new-window -n "NEWBOT" -t ${SESSION_NAME}:7
  tmux send-keys -t ${SESSION_NAME}:7 "source $ALANA_ENV; cd $ALANA_PATH/NEW_BOT/; sleep 5; gunicorn --workers=${BOT_WORKERS} http_bot:app --bind 0.0.0.0:5557" C-m
  tmux split-window -v -t ${SESSION_NAME}:7
  tmux send-keys -t ${SESSION_NAME}:7.1 "source $ALANA_ENV; cd $ALANA_PATH/NEW_BOT/Profiler; sleep 2; npm start" C-m
  tmux split-window -h -t ${SESSION_NAME}:7
  tmux send-keys -t ${SESSION_NAME}:7.2 "source $ALANA_ENV; cd $ALANA_PATH/NEW_BOT/NLU; sleep 10; python2 bot.py" C-m

  # Start out on the first window when we attach
  tmux select-window -t ${SESSION_NAME}:0
fi
unset TMUX
tmux a -t ${SESSION_NAME}
