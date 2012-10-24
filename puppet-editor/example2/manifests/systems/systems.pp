# Crichton, Admirable Source Configuration Management
# Copyright 2012 British Broadcasting Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#
node app001, app004 { include app::live::cwwtfpool1 }
node app016, app017 { include app::live::cwwtfpool2 }

node app101, app102 { include app::live::telhcpool1 }
node app103, app104 { include app::live::telhcpool2 }

node pal013, pal014 { include pal::live::cwwtfpool1 }
node pal113, pal114 { include pal::live::telhcpool1 }

node static003, static103 { include static::live::pool1 }
