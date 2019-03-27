/*
 * Copyright 2019 The FATE Authors. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.webank.ai.fate.core.storage.dtable;

import com.webank.ai.fate.core.constant.WorkMode;
import com.webank.ai.fate.core.utils.Configuration;

public class DTableFactory {

    public static DTable getDTable(){
        return getDTable(Configuration.getIntProperty("workMode"));
    }

    public static DTable getDTable(int workMode){
        DTable dTable;
        switch (workMode){
            case WorkMode.STANDALONE:
                dTable = new StandaloneDTable();
                break;
            case WorkMode.CLUSTER:
                dTable = new DistributedDTable();
                break;
            default:
                dTable = new StandaloneDTable();
                break;
        }
        return dTable;
    }
}
